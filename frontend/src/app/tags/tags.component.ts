import { Component, OnInit } from '@angular/core';
import { COMMA, ENTER, SPACE } from '@angular/cdk/keycodes';
import { MatChipInputEvent } from '@angular/material/chips';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-tags',
  templateUrl: './tags.component.html',
  styleUrls: ['./tags.component.scss']
})
export class TagsComponent implements OnInit {

  visible = true;
  selectable = true;
  removable = true;
  addOnBlur = true;
  tags;
  readonly separatorKeysCodes: number[] = [ENTER, COMMA, SPACE];

  constructor(private api: ApiService) { }

  public ngOnInit() {
    this.api.getTags()
      .subscribe((data) => {
        this.tags = data;
      });
  }

  public add(event: MatChipInputEvent): void {
    const input = event.input;
    const value = event.value;
    if ((value || '').trim()) {
      if (!this.isDuplicate(event.value)) {
        this.tags.push(value.trim());
        this.api.addTag({ tag: value })
          .subscribe(res => {
            console.log(res);
          });
      } else {
        alert('tag already present');
      }
    }
    if (input) {
      input.value = '';
    }

  }

  private isDuplicate(value) {
    const index = this.tags.findIndex((tag) => tag === value);
    if (index === -1) {
      return false;
    }
    return true;
  }

  public remove(tag): void {
    const index = this.tags.indexOf(tag);

    if (index >= 0) {
      this.tags.splice(index, 1);
    }

    this.api.removeTag(tag)
      .subscribe(res => {
        console.log(res);
      });
  }

}
