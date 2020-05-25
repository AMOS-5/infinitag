import { HttpClient } from '@angular/common/http';
import { IDocument } from '../models/IDocument.model';

import { Component, Input, OnChanges, OnInit, SimpleChanges, ViewChild } from '@angular/core';
import { MatSort } from '@angular/material/sort';
import { MatInput } from '@angular/material/input';
import { MatTableDataSource } from '@angular/material/table';
import { SelectionModel } from '@angular/cdk/collections';
import { MatSnackBar } from '@angular/material/snack-bar';

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
  @ViewChild(MatInput) input = MatInput;
  @Input() documents: Array<IDocument> | undefined;
  @Input() filter: string | undefined;
  dataSource = new MatTableDataSource();
  selection = new SelectionModel(true, []);



  public ngOnInit() {
    if (this.documents !== undefined) {
      this.documents.map((document: IDocument) => {
        document.creation_date = new Date(document.creation_date);
      });
      this.dataSource.data = this.documents;
      setTimeout(() => {
        this.dataSource.sort = this.sort;
      });
    }
    this.api.getTags()
      .subscribe((data: []) => {
        this.tags = data;
        this.selectedTags = this.tags;
      });
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

  /** Whether all currently displayed items are selected */
  isAllSelected() {
    const filteredData = this.dataSource.filteredData;
    for(let i = 0; i < filteredData.length; i++) {
      if(this.selection.selected.includes(filteredData[i]) == false) {
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


  addTagToDoc(iDoc, tag) {
    if(iDoc.tags.includes(tag) == false) {
      iDoc.tags.push(tag);
      iDoc.tags.sort();
      return iDoc;
    } else {
      this.snackBar.open('Tag already added to this doc', ``, { duration: 3000 });
      return null;
    }
  }

  applyTag(doc, tag) {
    doc = this.addTagToDoc(doc, tag);
    if(doc) {
      this.uploadService.patchTags(doc).subscribe(res => {

      });
    }
  }

  applyBulkTags(tag) {
    if(this.selection.selected.length == 0) {
      this.snackBar.open('no rows selected', ``, { duration: 3000 });
    }

    //send tags to backend here
    for(let i = 0; i < this.selection.selected.length; i++) {
      let doc = this.selection.selected[i];
      doc = this.addTagToDoc(doc, tag);
      if(doc) {
        this.uploadService.patchTags(doc).subscribe(res => {

        });
      }
    }
  }

  onKey(event) {
    this.selectedTags = this.search(event.target.value);
  }

  search(value: string) {
    const filter = value.toLowerCase();
    return this.tags.filter(option => option.toLowerCase().startsWith(filter));
  }
}

