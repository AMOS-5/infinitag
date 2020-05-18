import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from './../../environments/environment';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UploadService {

  
  constructor(private httpClient: HttpClient) { }

  postFile(file: File): Observable<object> {

    console.log("postFile" + file.name)
    const formData: FormData = new FormData();
    formData.append('fileKey', file, file.name);
    //formData.append('test', 'abc');
    return this.httpClient
      .post(`${environment.serverUrl}/upload`, formData, {
        reportProgress: true,
        observe: 'events'
      })
  }
}
