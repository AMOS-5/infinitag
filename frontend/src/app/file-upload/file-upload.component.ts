import { Component, OnInit } from '@angular/core';
import { UploadService } from '../services/upload.service';



@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent implements OnInit {
  files: FileList = null;

  constructor(private uploadService: UploadService) { }

  ngOnInit(): void {
  }

  onSelectFile(files: FileList) {
    this.files = files;
    for (let idx = 0; idx < files.length; idx++) {
      let file = files[idx];
      this.sendFileToService(file);
    }
  }

  sendFileToService(file: File) {
    this.uploadService.postFile(file).subscribe(data => {
        console.log("uploaded file successfully: " + file.name)
      }, error => {
        console.log(error);
      });
  }

}
