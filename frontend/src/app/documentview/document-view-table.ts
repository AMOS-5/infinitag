import {HttpClient} from '@angular/common/http';
import {IDocument} from '../models/IDocument.model';

import {Component, OnInit, ViewChild} from '@angular/core';
import {MatSort} from '@angular/material/sort';
import {MatTableDataSource} from '@angular/material/table';

import { environment } from './../../environments/environment';



/**
 * Component gets document data from the backend and displays it as a table
 */
@Component({
  selector: 'document-view-table',
  styleUrls: ['document-view-table.scss'],
  templateUrl: 'document-view-table.html',
})
export class DocumentViewTable implements OnInit {
  //defines order of columns
  displayedColumns: string[] = ['name', 'path', 'type', 'lang', 'size', 'createdAt'];


  constructor( private httpClient: HttpClient) {}

  @ViewChild(MatSort, {static: true}) sort: MatSort;
  dataSource = new MatTableDataSource();
  

  public ngOnInit() {
    this.httpClient.get(`${environment.apiUrl}/documents`)
      .subscribe((value: Array<IDocument>) => {
        value.map((doc) => {
          doc.createdAt = new Date(doc.createdAt)
        })
        this.dataSource.data = value;
      });
    setTimeout(() => {
      this.dataSource.sort = this.sort;
    });
  }
}

