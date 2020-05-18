import { Component, OnInit } from '@angular/core';
import { UploadService } from '../services/upload.service';
import { HttpEvent, HttpEventType } from '@angular/common/http';

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
export class FileUploadComponent implements OnInit {
  files: Array<IFile> = [];

  constructor(private uploadService: UploadService) { }

  ngOnInit(): void {
  }

  onSelectFile(files: FileList) {
    this.files = [];
    for (let idx = 0; idx < files.length; idx++) {
      let file: IFile = { file: files[idx], status: "enqueued", progress:0, icon:"schedule" };
      this.files.push(file);
      this.sendFileToService(file);
    }
  }

  sendFileToService(file: IFile) {
    this.uploadService.postFile(file.file).subscribe((event: HttpEvent<any>) => {
      switch (event.type) {
        case HttpEventType.Sent:
          file.status = "request send";
          break;
        case HttpEventType.ResponseHeader:
          file.status = "response received";
          break;
        case HttpEventType.UploadProgress:
          file.progress = Math.round(event.loaded / event.total * 100);
          file.status = "uploading...";
          file.icon = "cloud_upload";
          break;
        case HttpEventType.Response:
          file.status = "success";
          console.log('Document send', event.body);
          file.icon = "cloud_done";
          setTimeout(() => {
          }, 1500);
      }
    });
  }

}
