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

import {Component, Inject} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {TranslateService} from '@ngx-translate/core';
import {IFile} from '../app/models/IFile.model';
import {Utils} from '../app/services/utils.service';
import {of} from 'rxjs';

export interface UploadDialogData {
  files: Array<IFile>;
  progressMonitor: {
    progress: number;
    finished: number;
  };
}

@Component({
  selector: 'app-file-upload-dialog',
  templateUrl: 'file-upload.dialog.html',
})
export class FileUploadDialogComponent {

  constructor(
    public dialogRef: MatDialogRef<FileUploadDialogComponent>,
    public translate: TranslateService,
    private utils: Utils,
    @Inject(MAT_DIALOG_DATA) public data: UploadDialogData) {}

  onDialogButtonClick(response: string): void {
    console.log(response);
  }

  public cancelUpload(file: IFile) {
    file.progress = 100;
    file.status = 'CANCELLED';
    file.icon = 'cloud_done';
  }

  public cancelAll() {
    for (const file of this.data.files) {
      this.cancelUpload(file);
    }
  }
}
