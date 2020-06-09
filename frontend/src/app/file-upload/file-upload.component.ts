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
import { Component, OnInit } from '@angular/core';
import { UploadService } from '../services/upload.service';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

interface IFile {
  file: File;
  status: string;
  progress: number;
  icon: string;
}
@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})

/**
 * @class FileUploadComponent
 *
 * Component handles the file input and displaying the progress
 */
export class FileUploadComponent implements OnInit {
  files: Array<IFile> = [];

  constructor(private uploadService: UploadService) { }

  public ngOnInit(): void {}

  /**
   * @description
   * Gets called when the file input element is used, parses the files and sends them to sendFileToService()
   * @param {FileList} files: FileList from the input html element
   */
  public onSelectFile(files: FileList) {
    this.files = [];
    for (let idx = 0; idx < files.length; idx++) {
      let file: IFile = { file: files[idx], status: "enqueued", progress:0, icon:"schedule" };
      this.files.push(file);
      this.sendFileToService(file);
    }
  }

  /**
   * @description
   * Takes IFile, sends it to the uploadService and updates the progress accordingly
   * @param {IFile} file: IFile object containing the file to be send
   */
  private sendFileToService(file: IFile) {
    this.uploadService.postFile(file.file)
    .pipe(
      //catch errors
      catchError(error => {
        file.status = "failed(check console for info)";
        file.icon = "close";
        return throwError(error);
      })
    ).subscribe((event: HttpEvent<any>) => {
      switch (event.type) {
        case HttpEventType.Sent:
          file.status = "request send";
          break;
        case HttpEventType.ResponseHeader:
          file.status = "response received";
          break;
        case HttpEventType.UploadProgress:
          //update progress
          file.progress = Math.round(event.loaded / event.total * 100);
          file.status = "uploading...";
          file.icon = "cloud_upload";
          break;
        case HttpEventType.Response:
          file.status = "success";
          console.log('Document send', event.body);
          file.icon = "cloud_done";
          break;
      }
    })
  }

}
