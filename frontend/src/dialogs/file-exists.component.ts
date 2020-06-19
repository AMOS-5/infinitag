import {Component, Inject} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material/dialog';
import {TranslateService} from '@ngx-translate/core';

export interface DialogData {
  id: string;
  fid: string;
}

@Component({
  selector: 'app-file-exists-dialog',
  templateUrl: 'file-exists.dialog.html',
})
export class FileExistsDialogComponent {

  constructor(
    public dialogRef: MatDialogRef<FileExistsDialogComponent>,
    public translate: TranslateService,
    @Inject(MAT_DIALOG_DATA) public data: DialogData) {}

  onDialogButtonClick(response: string): void {
    this.dialogRef.close({response, id: this.data.id, fid: this.data.fid});
  }
}
