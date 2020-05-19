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
 * Component handleing the file input and displaying the progress
 */
export class FileUploadComponent implements OnInit {
  files: Array<IFile> = [];

  constructor(private uploadService: UploadService) { }

  public ngOnInit(): void {}

  /**
   * Gets called when the file input element is used, parses the files and sends them to sendFileToService()
   * @param files: FileList from the input html element
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
   * Takes IFile, sends it to the uploadService and updates the progress accordingly
   * @param file: IFile object containing the file to be send
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
