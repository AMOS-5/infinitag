import { HttpClient } from '@angular/common/http';
import { IDocument } from '../models/IDocument.model';

import { Component, Input, OnChanges, OnInit, SimpleChanges, ViewChild } from '@angular/core';
import { MatSort } from '@angular/material/sort';
import { MatInput } from '@angular/material/input';
import { MatTableDataSource } from '@angular/material/table';

import { ApiService } from '../services/api.service';



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
  constructor(private api: ApiService) { }
  // defines order of columns
  displayedColumns: string[] = ['title', 'type', 'language', 'size', 'creation_date', 'MyTags'];

  @ViewChild(MatSort, { static: true }) sort: MatSort;
  @ViewChild(MatInput) input = MatInput;
  @Input() documents: Array<IDocument> | undefined;
  @Input() filter: string | undefined;
  dataSource = new MatTableDataSource();



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

  onKey(event) {
    this.selectedTags = this.search(event.target.value);
  }

  search(value: string) {
    const filter = value.toLowerCase();
    return this.tags.filter(option => option.toLowerCase().startsWith(filter));
  }
}

