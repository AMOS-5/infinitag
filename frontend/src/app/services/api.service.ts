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
import { environment } from './../../environments/environment';
import { Observable } from 'rxjs';
import { IKeyWordModel } from './../models/IKeyWordModel.model'
/**
 *
 * @class ApiService
 *
 * Service handling communication regarding the keywords with the backend
 *
 */
@Injectable({
  providedIn: 'root'
})
export class ApiService {

  constructor(private http: HttpClient) { }

  public getUncategorizedDimensions() {
    return this.http.get(`${environment.serverUrl}/dims`);
  }

  public getUncategorizedKeywords() {
    return this.http.get(`${environment.serverUrl}/keys`);
  }

  public addUncategorizedDimension(dim): Observable<object> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
      })
    };
    return this.http.post(`${environment.serverUrl}/dims`, { dim: dim }, httpOptions);
  }

  public addUncategorizedKeyword(key): Observable<object> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
      })
    };
    return this.http.post(`${environment.serverUrl}/keys`, { key: key }, httpOptions);
  }

  public removeUncategorizedDimension(dim): Observable<object> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    };
    return this.http.delete(`${environment.serverUrl}/dims/${dim}`, httpOptions);
  }

  public removeUncategorizedKeyword(key): Observable<object> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    };
    return this.http.delete(`${environment.serverUrl}/keys/${key}`, httpOptions);
  }

  public getKeywordModels() {
    return this.http.get(`${environment.serverUrl}/models`);
  }

  public addKeywordModel(kwm: IKeyWordModel): Observable<object> {
    const dict = {
      "id" : kwm.id,
      "hierarchy" : kwm.hierarchy,
    };
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
      })
    };
    return this.http.post(`${environment.serverUrl}/models`, JSON.stringify(dict), httpOptions);
  }

  public removeKeywordModel(kwm: IKeyWordModel): Observable<object> {

    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
      })
    };
    console.log("deleting: ", kwm.id);
    return this.http.delete(`${environment.serverUrl}/models/${kwm.id}`, httpOptions);
  }
}
