import { Component, OnInit } from '@angular/core';
import { CdkDragDrop, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-keywords',
  templateUrl: './keywords.component.html',
  styleUrls: ['./keywords.component.scss']
})
export class KeywordsComponent implements OnInit {


  newDimension: string;
  newKeyword: string;

  uncatDimensions = []
  uncatKeywords = []



  constructor(private api: ApiService, private snackBar: MatSnackBar) { }

  ngOnInit(): void {
    this.api.getUncategorizedDimensions()
      .subscribe((data: []) => {
        this.uncatDimensions = data;
      });
    this.api.getUncategorizedKeywords()
      .subscribe((data: []) => {
        this.uncatKeywords = data;
      });
  }

  dropDim(event: CdkDragDrop<string[]>) {
    moveItemInArray(this.uncatDimensions, event.previousIndex, event.currentIndex);
  }

  dropKey(event: CdkDragDrop<string[]>) {
    moveItemInArray(this.uncatKeywords, event.previousIndex, event.currentIndex);
  }

  onDimEnter() {
    const dimFormatted = this.newDimension.trim().toLowerCase();
    console.log(dimFormatted);
    if(dimFormatted !== "") {
      if(!this.isDuplicate(this.uncatDimensions, dimFormatted)) {
        this.api.addUncategorizedDimension(dimFormatted)
          .subscribe(res => {
            this.uncatDimensions.push(dimFormatted)
            this.snackBar.open(`${dimFormatted} added into the database`, '', { duration: 3000 });
          });
      } else {
        this.snackBar.open(`${dimFormatted} already present`, '', { duration: 3000 });
      }
    }
    this.newDimension="";
  }

  onKeyEnter() {
    const keyFormatted = this.newKeyword.trim().toLowerCase();
    console.log(keyFormatted);
    if(keyFormatted !== "") {
      if(!this.isDuplicate(this.uncatKeywords, keyFormatted)) {
        this.api.addUncategorizedKeyword(keyFormatted)
          .subscribe(res => {
            this.uncatKeywords.push(keyFormatted)
            this.snackBar.open(`${keyFormatted} added into the database`, '', { duration: 3000 });
          });
      } else {
        this.snackBar.open(`${keyFormatted} already present`, '', { duration: 3000 });
      }
    }
    this.newKeyword="";
  }

  private isDuplicate(arr, value) {
    const index = arr.findIndex((elem) => elem === value);
    if (index === -1) {
      return false;
    }
    return true;
  }

  public deleteDimension(dimension: string) {
    const index = this.uncatDimensions.indexOf(dimension);

    if (index >= 0) {
      this.api.removeUncategorizedDimension(dimension)
      .subscribe(res => {
        this.uncatDimensions.splice(index, 1);
        this.snackBar.open(`${dimension} deleted from the database`, '', { duration: 3000 });
      });
    }
  }

  public deleteKeyword(keyword: string) {
    const index = this.uncatKeywords.indexOf(keyword);

    if (index >= 0) {
      this.api.removeUncategorizedKeyword(keyword)
      .subscribe(res => {
        this.uncatKeywords.splice(index, 1);
        this.snackBar.open(`${keyword} deleted from the database`, '', { duration: 3000 });
      });
    }
  }

}
