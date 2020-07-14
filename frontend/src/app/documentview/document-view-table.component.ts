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

import { IDocument } from '../models/IDocument.model';
import { IKeyword } from '../models/IKeyword.model';

import {
  Component,
  Input,
  OnChanges,
  OnInit,
  SimpleChanges,
  ViewChild,
  ElementRef,
  EventEmitter,
  Output
} from '@angular/core';
import { MatSort, Sort } from '@angular/material/sort';
import { MatTableDataSource, MatTable } from '@angular/material/table';
import { SelectionModel } from '@angular/cdk/collections';
import { MatSnackBar } from '@angular/material/snack-bar';
import { of, throwError, Observable, Subscription, interval } from 'rxjs';
import { ApiService } from '../services/api.service';
import { MatPaginator, PageEvent } from '@angular/material/paginator';
import { MatDialog } from '@angular/material/dialog';

import { UploadService } from '../services/upload.service';
import { FormBuilder } from '@angular/forms';
import { IKeywordListEntry } from '../models/IKeywordListEntry.model';

import { MatTabChangeEvent} from '@angular/material/tabs';

import * as moment from 'moment';
/**
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
  keywords: IKeywordListEntry[] = [];
  selectedKeywords: IKeywordListEntry[] = [];
  visible = true;

  editing = false;

  constructor(
    private api: ApiService,
    private uploadService: UploadService,
    private snackBar: MatSnackBar,
    public dialog: MatDialog
  ) {}
  // defines order of columns
  displayedColumns: string[] = ['select', 'title', 'type', 'language', 'size', 'last_modified', 'MyKeywords'];

  @ViewChild(MatSort, { static: true }) sort: MatSort;
  @ViewChild(MatTable, { static: true }) table: MatTable<any>;
  @ViewChild(MatPaginator) paginator: MatPaginator;

  interval: Subscription;
  @Input() documents: Array<IDocument> | undefined;
  @Input() pageSize: number | undefined;
  @Input() currentPage: number | undefined;
  @Input() sortField: string | undefined;
  @Input() sortOrder: string | undefined;
  @Input() totalPages: number | undefined;
  @Input() filter: string | undefined;

  @Output() syncRequested = new EventEmitter();
  @Output() pageEvent = new EventEmitter<PageEvent>();
  dataSource = new MatTableDataSource();
  selection = new SelectionModel(true, []);
  breakpoint: number;
  allData: any;
  searchString = '';
  startDate: string;
  endDate: string;
  KEYWORD_TYPE_COLORS = {
    MANUAL   : '#a6a6a6',
    KWM      : '#66ff66',
    ML       : '#3399ff',
    META     : '#e8453c'
  };

  KEYWORD_TYPE_TOOLTIPS = {
    MANUAL   : 'DOCUMENTS.TOOLTIP_MANUAL',
    KWM      : 'DOCUMENTS.TOOLTIP_KWM',
    ML       : 'DOCUMENTS.TOOLTIP_ML',
    META     : 'DOCUMENTS.TOOLTIP_META'
  };


  public ngOnInit() {
    this.setDatasource();
    this.api.getKeywordListEntries()
      .subscribe((data: []) => {
        this.keywords = data;
        this.selectedKeywords = this.keywords;
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
    console.log(this.documents)
    if (this.documents !== undefined) {
      this.documents.map((document: IDocument) => {
        document.creation_date = new Date(document.creation_date);
        document.last_modified = new Date(document.last_modified);
      });
      this.dataSource.data = this.documents;
      this.dataSource.paginator ? this.dataSource.paginator = this.paginator : null;
    }
  }


  /**
   * @description
   * Updates the documents list as well as the filter term
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
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(res.body);
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
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(res.body);
      if (this.selection.selected.length === 1) {
        link.setAttribute('download', this.selection.selected[0].id);
      } else {
        link.setAttribute('download', 'documents.zip');
      }
      link.click();
    });
  }

  /**
   * @description
   * Adds a new keyword to an IDocument object. Thorws an error if the keyword
   * is already added to the document
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
   */
  public applyKeyword(doc: IDocument, keyword: IKeywordListEntry) {
    let to_add = [keyword.id];
    to_add = to_add.concat(keyword.parents);

    for (let i = 0; i < to_add.length; i++) {
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
   * Gets called when the delete button is pressed on a mat-chip.
   * Removes the keyword from the document and sends the change to the backend.
   * @param keyword to be removed
   */
  public removeKeywordFromDocument(document: IDocument, keyword) {
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
   */
  public onKey(event) {
    this.selectedKeywords = this.search(event.target.value);
  }

  /**
   * @description
   * Searches the keywords list for a search term
   */
  private search(value: string) {
    const filter = value.toLowerCase();
    return this.keywords.filter(kw => kw.id.toLowerCase().startsWith(filter));
  }

   /**
    * @description
    * Gets page event from frontand and runs the iterator.
    */
  public paginate(e: PageEvent){
    this.currentPage = e.pageIndex;
    this.pageSize = e.pageSize;
    this.pageEvent.emit(e);
    this.api.getDocuments(this.currentPage, this.pageSize, this.sortField, this.sortOrder, this.searchString).subscribe((documents: any) => {
      this.documents = documents.docs;
      this.dataSource.data = this.documents;
    });
    return e;
  }

  public tabChanged(tabChangeEvent: MatTabChangeEvent): void {
    this.editing = tabChangeEvent.index > 0;
  }

  public sync() {
    console.log('Syncing....');
    // this.ngOnInit();
    this.selection = new SelectionModel(true, []);
    const syncEvent = {
      currentPage: this.currentPage,
      pageSize: this.pageSize
    };
    this.syncRequested.emit(syncEvent);
  }

  updateData(sort: Sort) {
    if (sort.direction !== ''){
      this.api.getDocuments(this.currentPage, this.pageSize, sort.active, sort.direction, this.searchString).subscribe((documents: any) => {
        this.documents = documents.docs;
        this.dataSource.data = this.documents;
      });
    }
  }

  updateSearchString(event) {
    this.searchString = event.target.value;
    this.api.getDocuments(this.currentPage, this.pageSize, this.sortField, this.sortOrder, this.searchString).subscribe((documents: any) => {
      this.documents = documents.docs;
      this.dataSource.data = this.documents;
      this.pageSize = documents.num_per_page;
      this.currentPage = documents.page;
      this.totalPages = documents.total_pages * documents.num_per_page;
    });
  }

  public getSizePresentation(size: number): string {
    const kilobytes = size / 1024;
    const megabytes = kilobytes / 1024;
    const gigabytes = megabytes / 1024;

    if (gigabytes > 1) {
      return `${gigabytes.toFixed(1)} GB`;
    } else if (megabytes > 1) {
      return `${megabytes.toFixed(1)} MB`;
    } else if (kilobytes > 1) {
      return `${kilobytes.toFixed(0)} KB`;
    }
    return `${size} B`;
  }

  updateDateString(event) {
    let mom:any = moment;
    this.startDate = mom.utc(event.startDate).toISOString().split('.')[0]+"Z";
    this.endDate = mom.utc(event.endDate).toISOString().split('.')[0]+"Z";

    console.log(this.startDate)
    console.log(this.endDate)
    this.api.getDocuments(this.currentPage, this.pageSize, this.sortField, this.sortOrder, this.searchString, this.startDate, this.endDate).subscribe((documents: any) => {
      this.documents = documents.docs;
      this.dataSource.data = this.documents;
      this.pageSize = documents.num_per_page;
      this.currentPage = documents.page;
      this.totalPages = documents.total_pages * documents.num_per_page;
    });
  }
}

