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
 * Component gets document data from the backend and displays it as a table
 */
@Component({
  selector: 'document-view-table',
  styleUrls: ['document-view-table.component.scss'],
  templateUrl: 'document-view-table.component.html',
})

export class DocumentViewTableComponent implements OnInit, OnChanges {

  tags: string[] = [];
  selectedTags: string[] = [];
  constructor(private api: ApiService, private uploadService: UploadService, private snackBar: MatSnackBar) { }
  // defines order of columns
  displayedColumns: string[] = ['select', 'title', 'type', 'language', 'size', 'creation_date', 'MyTags'];

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
    this.api.getTags()
      .subscribe((data: []) => {
        this.tags = data;
        this.selectedTags = this.tags;
      });
    this.breakpoint = (window.innerWidth <= 400) ? 1 : 6;
  }

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

  private onResize(event) {
    this.breakpoint = (event.target.innerWidth <= 400) ? 1 : 6;
  }

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

  /** Whether all currently displayed items are selected */
  isAllSelected() {
    const filteredData = this.dataSource.filteredData;
    for (let i = 0; i < filteredData.length; i++) {
      if (this.selection.selected.includes(filteredData[i]) === false) {
        return false;
      }
    }
    return true;
  }

  /** Selects all visible rows if they are not all selected; otherwise clear selection. */
  masterToggle() {
    this.isAllSelected() ?
      this.selection.clear() :
      this.dataSource.filteredData.forEach(row => this.selection.select(row));
  }


  addTagToDoc = (iDoc, tag): Observable<IDocument> => {
    if (iDoc.tags.includes(tag) === false) {
      iDoc.tags.push(tag);
      iDoc.tags.sort();
      return of(iDoc);
    } else {
      return throwError('Tag already added to ' + iDoc.title);
    }
  }

  applyTag(doc, tag) {
    this.addTagToDoc(doc, tag).subscribe(
      res => {
        this.uploadService.patchTags(res).subscribe(() => {
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

  applyBulkTags(tag) {
    if (this.selection.selected.length === 0) {
      this.snackBar.open('no rows selected', ``, { duration: 3000 });
    }
    this.selection.selected.forEach(doc => {
      this.applyTag(doc, tag);
    });
  }

  onKey(event) {
    this.selectedTags = this.search(event.target.value);
  }

  search(value: string) {
    const filter = value.toLowerCase();
    return this.tags.filter(option => option.toLowerCase().startsWith(filter));
  }
}

