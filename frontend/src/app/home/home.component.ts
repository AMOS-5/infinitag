import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { IDocument } from '../models/IDocument.model';
import { environment } from './../../environments/environment';
@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})

export class HomeComponent implements OnInit {
  public title = 'infinitag';
  public serverUrl = environment.serverUrl;
  public backendStatus = `${this.serverUrl}/health`;
  public documentsUrl = `${this.serverUrl}/documents`;
  public uploadUrl = `${this.documentsUrl}/upload`;
  public downloadUrl = `${this.documentsUrl}/download`;

  public serverStatus = 'DOWN';

  public documents: Array<IDocument> = [];
  public filterString = '';

  constructor(private httpClient: HttpClient) { }

  public ngOnInit(): void {
    this.httpClient.get(this.documentsUrl)
      .subscribe((value: Array<IDocument>) => {
        console.log(value)
        this.documents = value;
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

  public download(document: IDocument) {
    const url = `${this.downloadUrl}/${document.title}`;

    this.httpClient.get(url)
      .subscribe((response: any) => {
        console.log(response);
      });
  }
}
