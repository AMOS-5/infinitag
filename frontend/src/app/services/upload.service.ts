import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpResponse, HttpErrorResponse } from '@angular/common/http';
import { environment } from './../../environments/environment';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { IDocument } from './../models/IDocument.model'

@Injectable({
  providedIn: 'root'
})
export class UploadService {


  constructor(private httpClient: HttpClient) { }


  public postFile(file: File): Observable<object> {
      //console.log("postFile" + file.name)
      const formData: FormData = new FormData();
      formData.append('fileKey', file, file.name);
      //formData.append('test', 'abc');
      return this.httpClient
        .post(`${environment.serverUrl}/upload`, formData, {
          reportProgress: true,
          observe: 'events'
        });

  }

  public patchTags(iDoc: IDocument): Observable<object> {
    console.log("sending doc: " + iDoc.path)
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
      })
    };

    return this.httpClient.patch(`${environment.serverUrl}/changetags`, iDoc, httpOptions);
  }


}
