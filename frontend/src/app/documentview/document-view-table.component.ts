import { HttpClient } from '@angular/common/http';
import { IDocument } from '../models/IDocument.model';

import { Component, Input, OnChanges, OnInit, SimpleChanges, ViewChild } from '@angular/core';
import { MatSort } from '@angular/material/sort';
import { MatTableDataSource, MatTable } from '@angular/material/table';
import { SelectionModel } from '@angular/cdk/collections';
import { MatSnackBar } from '@angular/material/snack-bar';
import { of, throwError, Observable, Subscription, interval } from 'rxjs';
import { ApiService } from '../services/api.service';

import { UploadService } from '../services/upload.service';


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

  keywords: string[] = [];
  selectedKeywords: string[] = [];
  constructor(private api: ApiService, private uploadService: UploadService, private snackBar: MatSnackBar) { }
  // defines order of columns
  displayedColumns: string[] = ['select', 'title', 'type', 'language', 'size', 'creation_date', 'MyKeywords'];

  @ViewChild(MatSort, { static: true }) sort: MatSort;
  @ViewChild(MatTable, { static: true }) table: MatTable<any>;
  interval: Subscription;
  @Input() documents: Array<IDocument> | undefined;
  @Input() filter: string | undefined;
  dataSource = new MatTableDataSource();
  selection = new SelectionModel(true, []);
  breakpoint: number;


  public ngOnInit() {
    this.setDatasource();
    this.api.getUncategorizedKeywords()
      .subscribe((data: []) => {
        this.keywords = data;
        this.selectedKeywords = this.keywords;
      });
    this.breakpoint = (window.innerWidth <= 400) ? 1 : 6;
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

      this.dataSource.data = this.documents;
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
  * Adds a new keyword to an IDocument object. Thorws an error if the keyword
  * is already added to the document
  * @param {IDocument} document
  * @param {string} keyword
  * @returns {Observable} Observable of the document
  */
  private addKeywordToDoc = (iDoc, keyword): Observable<IDocument> => {
    if (iDoc.keywords.includes(keyword) === false) {
      iDoc.keywords.push(keyword);
      iDoc.keywords.sort();
      return of(iDoc);
    } else {
      return throwError('Keyword already added to ' + iDoc.title);
    }
  }

  /**
  * @description
  * Adds a keyword to a document, then sends a PATCH request to the backend
  * to update the document. If the request is succesfull the datasource gets
  * updated.
  * @param {IDocument} document
  * @param {string} keyword
  */
  public applyKeyword(doc, keyword) {
    this.addKeywordToDoc(doc, keyword).subscribe(
      res => {
        this.uploadService.patchKeywords(res).subscribe(() => {
          const index = this.documents.findIndex(document => document.id === doc.id);
          const data = this.dataSource.data;
          data.splice(index, 1);
          this.dataSource.data = data;
          data.splice(index, 0, doc);
          this.dataSource.data = data;
        });
      },
      err => this.snackBar.open(err, ``, { duration: 3000 })
    );
  }

   /**
  * @description
  * Adds a keyword to all selected documents.
  * @param {string} keyword
  */
  public applyBulkKeywords(keyword) {
    if (this.selection.selected.length === 0) {
      this.snackBar.open('no rows selected', ``, { duration: 3000 });
    }
    this.selection.selected.forEach(doc => {
      this.applyKeyword(doc, keyword);
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
  * @returns {string[]} List of keywords matching search term
  */
  private search(value: string) {
    const filter = value.toLowerCase();
    return this.keywords.filter(option => option.toLowerCase().startsWith(filter));
  }
}

