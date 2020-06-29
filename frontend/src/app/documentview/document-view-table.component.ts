/**
 * @license
 * InfiniTag
 * Copyright (c) 2020 AMOS-5.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

import { HttpClient, HttpResponse } from '@angular/common/http';
import { IDocument } from '../models/IDocument.model';
import { IKeyword } from '../models/IKeyword.model';

import { Component, Input, OnChanges, OnInit, SimpleChanges, ViewChild, ElementRef } from '@angular/core';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource, MatTable } from '@angular/material/table';
import { SelectionModel } from '@angular/cdk/collections';
import { MatSnackBar } from '@angular/material/snack-bar';
import { of, throwError, Observable, Subscription, interval } from 'rxjs';
import { ApiService } from '../services/api.service';
import { MatAutocompleteSelectedEvent, MatAutocomplete } from '@angular/material/autocomplete';
import { MatChipInputEvent } from '@angular/material/chips';
import { startWith, map } from 'rxjs/operators';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { MatPaginator, PageEvent } from '@angular/material/paginator';
import { MatDialog } from '@angular/material/dialog';

import { UploadService } from '../services/upload.service';
import { FormBuilder } from '@angular/forms';
import { FormControl } from '@angular/forms';

import { ITaggingMethod } from '../models/ITaggingMethod';
import { ITaggingRequest } from '../models/ITaggingRequest.model';
import { IKeywordListEntry } from '../models/IKeywordListEntry.model'

import { DialogData, AutomatedTaggingParametersDialog } from '../../dialogs/automated-tagging-parameters.component'

/**
 * @class DocumentViewTableComponent
 *
 * Component gets document data from the backend and displays it as a table.
 * The data can be filtered through a search bar and new tags can be added
 * to the documents
 */
@Component({
  selector: 'document-view-table',
  styleUrls: ['document-view-table.component.scss'],
  templateUrl: 'document-view-table.component.html',
})

export class DocumentViewTableComponent implements OnInit, OnChanges {
  //Keywords displayed in the menu
  keywords: IKeywordListEntry[] = [];
  selectedKeywords: IKeywordListEntry[] = [];

  keywordModels: any = [];
  kwmToAdd = [];

  visible = true;
  selectable = true;
  removable = true;
  applyingTaggingMechanism = false;
  separatorKeysCodes: number[] = [ENTER, COMMA];
  bulkKwCtrl = new FormControl();
  filteredBulkKeywords: Observable<IKeywordListEntry[]>;
  selectedBulkKeywords: IKeywordListEntry[] = [];

  @ViewChild('bulkKWInput') KWInput: ElementRef<HTMLInputElement>;
  @ViewChild('auto') matAutocomplete: MatAutocomplete;

  constructor(
    private api: ApiService,
    private uploadService: UploadService,
    private snackBar: MatSnackBar,
    private formBuilder: FormBuilder,
    public dialog: MatDialog
  ) {


    this.taggingForm = this.formBuilder.group({
      taggingMethod: this.selectedTaggingMethod,
      keywordModel: undefined,
      documents: [],
      bulkKeywords: []
    });
    this.filteredBulkKeywords = this.bulkKwCtrl.valueChanges.pipe(
      startWith(null),
      map((selectedBulkKeyword: IKeywordListEntry | null) => selectedBulkKeyword ? this._filter(selectedBulkKeyword) : this.selectedKeywords.slice()));
  }
  // defines order of columns
  displayedColumns: string[] = ['select', 'title', 'type', 'language', 'size', 'creation_date', 'MyKeywords'];

  @ViewChild(MatSort, { static: true }) sort: MatSort;
  @ViewChild(MatTable, { static: true }) table: MatTable<any>;
  @ViewChild(MatPaginator) paginator: MatPaginator;

  interval: Subscription;
  @Input() documents: Array<IDocument> | undefined;
  @Input() filter: string | undefined;
  dataSource = new MatTableDataSource();
  selection = new SelectionModel(true, []);
  breakpoint: number;
  allData: any;
  pageSize = 10;
  currentPage = 0;
  totalSize;
  end: number;
  start: number;

  KEYWORD_TYPE_COLORS = {
    MANUAL   : '#a6a6a6',
    KWM       : '#66ff66',
    ML        : '#3399ff',
  };

  public taggingMethods: Array<ITaggingMethod> = [
    {
      name: 'Keyword Model',
      type: 'KWM'
    },
    {
      name: 'Automated',
      type: 'ML'
    }
  ];

  public taggingForm;

  public selectedTaggingMethod = this.taggingMethods[0];


  public ngOnInit() {
    this.setDatasource();
    this.api.getKeywordListEntries()
      .subscribe((data: []) => {
        this.keywords = data;
        this.selectedKeywords = this.keywords;
      });

    this.api.getKeywordModels()
      .subscribe((data: any) => {
        this.keywordModels = data;
      });
    this.breakpoint = (window.innerWidth <= 400) ? 1 : 6;

    // tell MatTableDataSource how an entry should be searched for given a filter string
    this.dataSource.filterPredicate =
    (doc: IDocument, filter: string) =>
    {
      return  doc.title.includes(filter) === true ||
              doc.language.includes(filter) === true ||
              doc.size.toString().includes(filter) === true ||
              doc.type.includes(filter) === true ||
              doc.keywords.filter(kw => kw.value.includes(filter)).length !== 0;
    };
  }

  /**
  * @description
  * Sets the data variable of this components MatTableDataSource instance
  */
  public setDatasource() {
    if (this.documents !== undefined) {
      this.documents.map((document: IDocument) => {
        document.creation_date = new Date(document.creation_date);
      });

      this.allData = this.documents;
      this.dataSource.paginator = this.paginator;
      this.totalSize = this.allData.length;
      this.iterator();
      setTimeout(() => {
        this.dataSource.sort = this.sort;
      });
    }
  }


  /**
  * @description
  * Updates the documents list as well as the filter term
  * @param {SimpleChanges} changes
  */
  public ngOnChanges(changes: SimpleChanges): void {
    if (changes.documents) {
      this.documents = changes.documents.currentValue;
      this.ngOnInit();
    }

    if (changes.filter) {
      this.dataSource.filter = changes.filter.currentValue;
    }
  }

  public focus(event) {
    setTimeout(() => {
      event.target.focus();
    }, 0);
  }


  /**
  * @description
  * Checks if all currently displayed items are selected
  * @returns true if the items are selected, false otherwise
  */
  public isAllSelected() {
    const filteredData = this.dataSource.filteredData;
    for (let i = 0; i < filteredData.length; i++) {
      if (this.selection.selected.includes(filteredData[i]) === false) {
        return false;
      }
    }
    return true;
  }

  /**
  * @description
  * Selects all visible rows if they are not all selected; otherwise clear selection.
  */
  public masterToggle() {
    this.isAllSelected() ?
      this.selection.clear() :
      this.dataSource.filteredData.forEach(row => this.selection.select(row));
  }

  /**
  * @description
  * Download a single document from the server and opens a save file dialog
  * @param {IDocument} document to download
  */
  public download(iDoc: IDocument) {
    this.uploadService.getFiles([iDoc]).subscribe(res => {
      var link = document.createElement('a');
      link.href = window.URL.createObjectURL(res.body);;
      link.setAttribute('download', iDoc.id);
      link.click();
    });
  }

  /**
  * @description
  * Downloads all selected documents from the server as a zip file
  * and opens a save file dialog.
  */
  public downloadBulk() {
    if (this.selection.selected.length === 0) {
      this.snackBar.open('no rows selected', ``, { duration: 3000 });
      return;
    }

    this.uploadService.getFiles(this.selection.selected).subscribe(res => {
      var link = document.createElement('a');
      link.href = window.URL.createObjectURL(res.body);
      if(this.selection.selected.length === 1) {
        link.setAttribute('download', this.selection.selected[0].id);
      } else {
        link.setAttribute('download', "documents.zip");
      }
      link.click();
    });
  }

  /**
  * @description
  * Adds a new keyword to an IDocument object. Thorws an error if the keyword
  * is already added to the document
  * @param {IDocument} document
  * @param {string} keyword
  * @returns {Observable} Observable of the document
  */
  private addKeywordToDoc = (iDoc: IDocument, keyword: IKeyword): Observable<IDocument> => {
    if (iDoc.keywords.filter(kw => kw.value === keyword.value).length === 0) {
      iDoc.keywords.push(keyword);
      iDoc.keywords.sort((a, b) => a.value.localeCompare(b.value));
      return of(iDoc);
    } else {
      return throwError('Keyword ' + keyword.value + ' already added to ' + iDoc.title);
    }
  }

  /**
  * @description
  * Adds a keyword and all its parents to a document, then sends a PATCH request to the backend
  * to update the document. If angular compile switch to browserthe request is succesfull the datasource gets
  * updated.
  * @param {IDocument} document
  * @param {IKeywordListEntry} keyword
  */
  public applyKeyword(doc: IDocument, keyword: IKeywordListEntry) {
    let to_add = [keyword.id]
    to_add = to_add.concat(keyword.parents)

    for(let i = 0; i < to_add.length; i++) {
      const kw: IKeyword = {value: to_add[i], type: 'MANUAL'};
      this.addKeywordToDoc(doc, kw).subscribe(
        res => {
          doc = res;
        },
        err => this.snackBar.open(err, ``, { duration: 3000 })
      );
    }

    this.uploadService.patchKeywords(doc).subscribe(() => {
      const index = this.documents.findIndex(document => document.id === doc.id);
      const data = this.dataSource.data;
      data.splice(index, 1);
      this.dataSource.data = data;
      data.splice(index, 0, doc);
      this.dataSource.data = data;
    });


  }

  /**
 * @description
 * Adds a keyword and its parents to all selected documents.
 */
  public applyBulkKeywords() {
    if (this.selection.selected.length === 0) {
      this.snackBar.open('no rows selected', ``, { duration: 3000 });
      return;
    }
    this.selectedBulkKeywords.forEach(keyword => {
      if (!this.selectedKeywords.includes(keyword)) {
        this.api.addUncategorizedKeyword(keyword.id).subscribe(() => {

        });
      }
      this.selection.selected.forEach(doc => {
        this.applyKeyword(doc, keyword);
      });
    });
    this.selectedBulkKeywords = [];
  }

  /**
  * @description
  * Gets called when the delete button is pressed on a mat-chip.
  * Removes the keyword from the document and sends the change to the backend.
  * @param {IDocument} document the keyword should be removed from
  * @param keyword to be removed
  */
  removeKeywordFromDocument(document: IDocument, keyword) {
    const index = document.keywords.indexOf(keyword);
    if (index >= 0) {
      document.keywords.splice(index, 1);
    }

    this.uploadService.patchKeywords(document).subscribe(res => {

    });
  }

  /**
  * @description
  * Gets called when a key is pressed while the search field for the keywords
  * is in focus. Updates the filter term.
  * @param event
  */
  public onKey(event) {
    this.selectedKeywords = this.search(event.target.value);
  }

  /**
  * @description
  * Searches the keywords list for a search term
  * @param {string} search term
  * @returns {IKeywordListEntry[]} List of keywords whose id starts with search term
  */
  private search(value: string) {
    const filter = value.toLowerCase();
    return this.keywords.filter(kw => kw.id.toLowerCase().startsWith(filter));
  }

  public changeTaggingMethod(event: any) {
    this.selectedTaggingMethod = event.value;
  }

  private  applyTaggingMethod(taggingData: ITaggingRequest) {
    this.applyingTaggingMechanism = true;
    taggingData.documents = this.selection.selected;
    this.api.applyTaggingMethod(taggingData).subscribe( (response: any) => {
      if (response.status === 200) {
        this.api.getDocuments().subscribe((documents: Array<IDocument>) => {
          this.documents = documents;
          this.setDatasource();
        });
      }
      this.applyingTaggingMechanism = false;
      this.selection = new SelectionModel(true, []);
    });
  }

  /**
   * Upon submitting the tagging mechanism, the method will be applied and the documents
   * will be fetched again to update the table
   */
  public onSubmit(taggingData: ITaggingRequest) {
    if(taggingData.taggingMethod.name === "Automated") {
      const dialogRef = this.dialog.open(AutomatedTaggingParametersDialog, {
        width: '300px',
        data: {numClusters: 5, numKeywords: 5}
      });

      dialogRef.afterClosed().subscribe((result: DialogData) => {
        if(result === undefined) return; // cancel was pressed

        result.numClusters = Number(result.numClusters)
        result.numKeywords = Number(result.numKeywords)

        if(result.numClusters === 0 || result.numKeywords === 0) { //happens if an empty string is inserted
          this.snackBar.open('invalid parameters', ``, { duration: 3000 });
          return;
        }

        taggingData.options = result;

        this.applyTaggingMethod(taggingData);
      });
    } else {
      this.applyTaggingMethod(taggingData);
    }
  }


  add(event: MatChipInputEvent): void {
    const input = event.input;
    const value = event.value;

    if ((value || '').trim()) {
      let kw: IKeywordListEntry = {id: value, kwm: null, parents: []}
      this.selectedBulkKeywords.push(kw);
    }

    // Reset the input value
    if (input) {
      input.value = '';
    }
    this.bulkKwCtrl.setValue(null);
  }

  remove(keyword: IKeywordListEntry): void {
    const index = this.selectedBulkKeywords.indexOf(keyword);

    if (index >= 0) {
      this.selectedBulkKeywords.splice(index, 1);
    }
  }

  selected(event: MatAutocompleteSelectedEvent): void {
    this.selectedBulkKeywords.push(event.option.value);
    this.KWInput.nativeElement.value = '';
    this.bulkKwCtrl.setValue(null);
  }

  private _filter(value): IKeywordListEntry[] {
    let filterValue;
    if(typeof(value) === "string") {
      filterValue = value.toLowerCase();
    } else {
      filterValue = value.id.toLowerCase();
    }
    return this.selectedKeywords.filter(keyword => keyword.id.toLowerCase().indexOf(filterValue) === 0);
  }

   /**
    * @description
    * Gets page event from frontand and runs the iterator.
    * @returns {object} PageEvent e
    */
  public handlePage(e: PageEvent){
    this.currentPage = e.pageIndex;
    this.pageSize = e.pageSize;
    this.iterator();
    return e;
  }

  /**
  * @description
  * Updates the datasource with current documents.
  * @returns {void}
  */

  private iterator() {
    this.end = (this.currentPage + 1) * this.pageSize;
    this.start = this.currentPage * this.pageSize;
    const part = this.allData.slice(this.start, this.end);
    this.dataSource.data = part;
  }
}
