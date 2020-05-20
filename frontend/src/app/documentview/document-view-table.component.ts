import {HttpClient} from '@angular/common/http';
import {IDocument} from '../models/IDocument.model';

import {Component, Input, OnChanges, OnInit, SimpleChanges, ViewChild} from '@angular/core';
import {MatSort} from '@angular/material/sort';
import {MatTableDataSource} from '@angular/material/table';

import { environment } from './../../environments/environment';



/**
 * Component gets document data from the backend and displays it as a table
 */
@Component({
  selector: 'document-view-table',
  styleUrls: ['document-view-table.component.scss'],
  templateUrl: 'document-view-table.component.html',
})
export class DocumentViewTableComponent implements OnInit, OnChanges {
  // defines order of columns
  displayedColumns: string[] = ['name', 'path', 'type', 'lang', 'size', 'createdAt', 'MyTags'];

  constructor() {}

  @ViewChild(MatSort, {static: true}) sort: MatSort;
  @Input() documents: Array<IDocument> | undefined;
  @Input() filter: string | undefined;
  dataSource = new MatTableDataSource();

  public ngOnInit() {
    if (this.documents !== undefined) {
      this.documents.map( (document: IDocument) => {
      document.createdAt = new Date(document.createdAt);
    });
      this.dataSource.data = this.documents;
      setTimeout(() => {
        this.dataSource.sort = this.sort;
      });
    }
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
}

