import {HttpClient} from '@angular/common/http';
import {IDocument} from '../models/IDocument.model';

import {Component, Input, OnChanges, OnInit, SimpleChanges, ViewChild} from '@angular/core';
import {MatSort} from '@angular/material/sort';
import {MatTableDataSource} from '@angular/material/table';
import {SelectionModel} from '@angular/cdk/collections';
import { MatSnackBar } from '@angular/material/snack-bar';

import { environment } from './../../environments/environment';

import { UploadService } from '../services/upload.service';


/**
 * Component gets document data from the backend and displays it as a table
 */
@Component({
  selector: 'document-view-table',
  styleUrls: ['document-view-table.component.scss'],
  templateUrl: 'document-view-table.component.html',
})
export class DocumentViewTableComponent implements OnInit, OnChanges {
  // defines order of columns
  displayedColumns: string[] = ['select', 'name', 'type', 'lang', 'size', 'createdAt', 'MyTags'];

  constructor(private snackBar: MatSnackBar, private uploadService: UploadService) {}

  @ViewChild(MatSort, {static: true}) sort: MatSort;
  @Input() documents: Array<IDocument> | undefined;
  @Input() filter: string | undefined;
  dataSource = new MatTableDataSource();
  selection = new SelectionModel(true, []);

  public ngOnInit() {
    if (this.documents !== undefined) {
      this.documents.map( (document: IDocument) => {
      document.createdAt = new Date(document.createdAt);
    });
      this.dataSource.data = this.documents;
      setTimeout(() => {
        this.dataSource.sort = this.sort;
      });
    }
  }

  public ngOnChanges(changes: SimpleChanges): void {
    if (changes.documents) {
      this.documents = changes.documents.currentValue;
      this.ngOnInit();
    }

    if (changes.filter) {
      this.dataSource.filter = changes.filter.currentValue;
    }
  }

  /** Whether all currently displayed items are selected */
  isAllSelected() {
    const filteredData = this.dataSource.filteredData;
    for(let i = 0; i < filteredData.length; i++) {
      if(this.selection.selected.includes(filteredData[i]) == false) {
        return false;
      }
    }
    return true;
  }

  /** Selects all visible rows if they are not all selected; otherwise clear selection. */
  masterToggle() {
    this.isAllSelected() ?
        this.selection.clear() :
        this.dataSource.filteredData.forEach(row => this.selection.select(row));
  }


  applyBulkTags() {
    if(this.selection.selected.length == 0) {
      this.snackBar.open('no rows selected', ``, { duration: 3000 });
    }

    //send tags to backend here
    //console.log(this.selection.selected)
    for(let i = 0; i < this.selection.selected.length; i++) {
      let doc = this.selection.selected[i];
      //console.log(doc);
      doc.tags.push("test");
      this.uploadService.patchTags(doc).subscribe(res => {

      });
    }
  }

}

