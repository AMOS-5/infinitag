import {Component} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {IDocument} from '../models/IDocument.model';

import { environment } from './../../environments/environment';



/**
 * Component gets document data from the backend and displays it as a table
 */
@Component({
  selector: 'document-view-table',
  styleUrls: ['document-view-table.scss'],
  templateUrl: 'document-view-table.html',
})
export class DocumentViewTable {
  //defines order of columns
  displayedColumns: string[] = ['name', 'path', 'type', 'lang', 'size', 'createdAt'];

  public documents: Array<IDocument> = [];

  constructor( private httpClient: HttpClient) {}

  public ngOnInit(): void {
    this.httpClient.get(`${environment.apiUrl}/documents`)
      .subscribe((value: Array<IDocument>) => {
        this.documents = value;
        /*this.documents.forEach(function (doc) {
          console.log(doc);
        });*/
      });
  }
}

