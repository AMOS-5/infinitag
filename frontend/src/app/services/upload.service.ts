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

import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';
import { IDocument } from '../models/IDocument.model';
import {IFile} from '../models/IFile.model';


/**
 *
 * Service handling uploading and updating documents
 *
 */
@Injectable({
  providedIn: 'root'
})
export class UploadService {
  constructor(private httpClient: HttpClient) { }

  public postFile(file: IFile): Observable<object> {
      const formData: FormData = new FormData();
      const fileData: File = file.file;
      formData.append('fid', file.fid);
      formData.append('fileKey', fileData, fileData.name);
      return this.httpClient
        .post(`${environment.serverUrl}/upload`, formData, {
          reportProgress: true,
          observe: 'events'
        });
  }

  public patchFile(file: IFile) {
    const formData: FormData = new FormData();
    const fileData: File = file.file;
    formData.append('fid', file.fid);
    formData.append('fileKey', fileData, fileData.name);
    return this.httpClient
      .patch(`${environment.serverUrl}/upload`, formData, {
        reportProgress: true,
        observe: 'events'
      });
  }

  public putFile(file: IFile) {
    const formData: FormData = new FormData();
    const fileData: File = file.file;
    formData.append('fileKey', fileData, fileData.name);
    formData.append('fid', file.fid);
    return this.httpClient
      .put(`${environment.serverUrl}/upload`, formData, {
        reportProgress: true,
        observe: 'events'
      });
  }

  public getFiles(iDocs: IDocument[]): Observable<any> {
    return this.httpClient.post(`${environment.serverUrl}/download`, iDocs, {
      observe: 'response',
      responseType: 'blob'
    });
  }

  public deleteFile(file: IFile) {
    return this.httpClient.delete(`${environment.serverUrl}/documents/${file.file.name}`);
  }

  public patchKeywords(iDoc: IDocument): Observable<object> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
      })
    };

    return this.httpClient.patch(`${environment.serverUrl}/changekeywords`, iDoc, httpOptions);
  }


}
