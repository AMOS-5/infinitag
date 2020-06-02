import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from './../../environments/environment';
import { Observable } from 'rxjs';

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
}
