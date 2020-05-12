import { Component, OnInit } from '@angular/core';
import { COMMA, ENTER, SPACE } from '@angular/cdk/keycodes';
import { MatChipInputEvent } from '@angular/material/chips';
import { ITag } from '../models/ITag.model';
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
  readonly separatorKeysCodes: number[] = [ENTER, COMMA, SPACE];

  tags: ITag[] = [];

  constructor(private api: ApiService) { }

  public ngOnInit() {
    this.api.getTags()
      .subscribe((data: Array<ITag>) => {
        this.tags = data;
      });
  }

  public add(event: MatChipInputEvent): void {
    const input = event.input;
    const value = event.value;
    if (value != '') {
      this.api.addTag({ name: value })
        .subscribe(res => {
          if ((value || '').trim()) {
            this.tags.push({ name: value.trim() });
          }
          if (input) {
            input.value = '';
          }
          console.log(res);
        });
    }
  }

  public remove(tag: ITag): void {
    this.api.removeTag(tag)
      .subscribe(res => {
        const index = this.tags.indexOf(tag);

        if (index >= 0) {
          this.tags.splice(index, 1);
        }
        console.log(res);
      });
  }

}
