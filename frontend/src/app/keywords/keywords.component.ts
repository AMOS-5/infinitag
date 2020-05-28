import { Component, OnInit } from '@angular/core';
import {CdkDragDrop, moveItemInArray, transferArrayItem} from '@angular/cdk/drag-drop';

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

  dropDim(event: CdkDragDrop<string[]>) {
    moveItemInArray(this.uncatDimensions, event.previousIndex, event.currentIndex);
  }

  dropKey(event: CdkDragDrop<string[]>) {
    moveItemInArray(this.uncatKeywords, event.previousIndex, event.currentIndex);
  }


  constructor() { }

  ngOnInit(): void {
  }

  onDimEnter() {
    console.log(this.newDimension);
    this.uncatDimensions.push(this.newDimension)
    this.newDimension="";
  }

  onKeyEnter() {
    console.log(this.newKeyword);
    this.uncatKeywords.push(this.newKeyword)
    this.newKeyword="";
  }

}
