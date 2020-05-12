import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from './../../environments/environment';
import { ITag } from '../models/ITag.model';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  constructor(private http: HttpClient) { }

  getTags() {
    return this.http.get(`${environment.serverUrl}/tags`);
  }

  addTag(tag: ITag): Observable<object> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
      })
    };
    return this.http.post(`${environment.serverUrl}/tags`, tag, httpOptions);
  }

  removeTag(tag: ITag): Observable<object> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    };
    return this.http.delete(`${environment.serverUrl}/tags/${tag.name}`, httpOptions);
  }
}
