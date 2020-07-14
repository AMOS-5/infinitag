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
import {Component, EventEmitter, Output} from '@angular/core';
import { UploadService } from '../services/upload.service';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { TranslateService } from '@ngx-translate/core';
import { MatDialog } from '@angular/material/dialog';
import { DialogData, FileExistsDialogComponent } from '../../dialogs/file-exists.component';
import { IFile } from '../models/IFile.model';
import { Utils } from '../services/Utils.service';
import { FileUploadDialogComponent, UploadDialogData } from '../../dialogs/file-upload.dialog.component';



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
export class FileUploadComponent {
  files: Array<IFile> = [];
  @Output() uploadFinished = new EventEmitter<any>();
  public progressMonitor = {
    progress: 0,
    finished: 0
  };

  constructor(
    private uploadService: UploadService,
    private translate: TranslateService,
    public dialog: MatDialog,
    public utils: Utils) {
  }

  openExistsDialog(dialogData: DialogData): void {
    const dialogRef = this.dialog.open(FileExistsDialogComponent, {
      width: '500px',
      data: dialogData
    });

    dialogRef.afterClosed().subscribe((result: { response: string, id: string, fid: string }) => {
      const file: IFile | undefined = this.files.find((f: IFile) => f.fid === result.fid);
      this.resendFile(result, file);
    });
  }

  openUploadDialog(dialogData: UploadDialogData): void {
    const dialogRef = this.dialog.open(FileUploadDialogComponent, {
      width: '1200px',
      data: dialogData
    });

    dialogRef.afterClosed()
      .subscribe( () => {
        this.uploadFinished.emit();
        this.cleanUpCancelledFiles(dialogData.files);
      });
  }

  public cleanUpCancelledFiles(files: Array<IFile>) {
    for (const file of files) {
      if (file.status === 'CANCELLED') {
        this.uploadService.deleteFile(file).subscribe( (result) => {
          console.log(result);
        });
      }

    }
  }

  public resendFile(requestType: { response: string }, file: IFile) {
    if (file !== undefined) {
      if (requestType.response === 'overwrite') {
        this.uploadService.patchFile(file)
          .subscribe((event: HttpEvent<any>) => {
            this.handleFileSend(event, file);
          });
      } else if (requestType.response === 'add') {
        this.uploadService.putFile(file)
          .subscribe((event: HttpEvent<any>) => {
            this.handleFileSend(event, file);
          });
      } else {
        file.status = 'CANCELLED';
        file.icon = 'cloud_done';
      }
    }
  }

  /**
   * @description
   * Gets called when the file input element is used, parses the files and sends them to sendFileToService()
   * @param {FileList} files: FileList from the input html element
   */
  public onSelectFile(files: FileList) {
    this.files = [];
    for (let idx = 0; idx < files.length; idx++) {
      const file: IFile = {file: files[idx], status: 'ENQUEUED', progress: 0, icon: 'schedule', fid: this.utils.uuid4()};
      this.files.push(file);
      this.sendFileToService(file);
    }
    const dialogData: UploadDialogData = {
      files: this.files,
      progressMonitor: this.progressMonitor
    };
    this.openUploadDialog(dialogData);
  }

  /**
   * @description
   * Takes IFile, sends it to the uploadService and updates the progress accordingly
   * @param {IFile} file: IFile object containing the file to be send
   */
  private sendFileToService(file: IFile) {
    if (file.status !== 'CANCELLED') {
      console.log(file.status);
      this.uploadService.postFile(file)
      .pipe(
        // catch errors
        catchError(error => {
          file.status = 'ERROR';
          file.icon = 'close';
          return throwError(error);
        })
      ).subscribe((event: HttpEvent<any>) => {
      this.handleFileSend(event, file);
    });
    }


  }

  private handleFileSend(event: HttpEvent<any>, file: IFile) {
    if (file.status !== 'CANCELLED') {
      switch (event.type) {
      case HttpEventType.Sent:
        file.status = 'REQUEST_SEND';
        break;
      case HttpEventType.ResponseHeader:
        file.status = 'RESPONSE_RECEIVED';
        break;
      case HttpEventType.UploadProgress:
        // update progress
        file.progress = Math.round(event.loaded / event.total * 100);
        this.progressMonitor.progress += file.progress;
        file.status = 'UPLOADING';
        file.icon = 'cloud_upload';
        break;
      case HttpEventType.Response:
        if (event.status === 207) {
          const id = event.body.id;
          const fid = event.body.fid;
          const dialogData: DialogData = {
            id,
            fid
          };
          this.openExistsDialog(dialogData);
        } else {
          file.status = 'SUCCESS';
          file.icon = 'cloud_done';
          this.progressMonitor.finished++;
        }
        break;
    }
    }
  }

}
