import {Component, OnInit} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {IDocument} from './models/IDocument.model';

import { environment } from './../environments/environment';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  public title = 'infinitag';
  
  public backendStatus = `${environment.apiUrl}/health`;
  public documentsUrl = `${environment.apiUrl}/documents`;
  public uploadUrl = `${this.documentsUrl}/upload`;
  public downloadUrl = `${this.documentsUrl}/download`;

  public serverStatus = 'DOWN';

  public documents: Array<IDocument> = [];

  constructor( private httpClient: HttpClient) {}

  public ngOnInit(): void {
    this.httpClient.get(this.backendStatus)
      .subscribe((value: {status: string}) => {
        this.serverStatus = value.status;
      });
  }

  public handleFileInput(files: FileList) {
    const file: File = files[0];
    const formData: FormData = new FormData();
    formData.append('file', file, file.name);
    this.httpClient.post(this.uploadUrl, formData)
      .subscribe((response: IDocument) => {
        this.documents.push(response);
      });
  }

  /*public download(document: IDocument) {
    const url = `${this.downloadUrl}/${document.name}`;

    this.httpClient.get(url)
      .subscribe((response: any) => {
        console.log(response);
      });
  }*/
}
