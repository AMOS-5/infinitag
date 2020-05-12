import { Component, OnInit } from '@angular/core';
import { COMMA, ENTER, SPACE } from '@angular/cdk/keycodes';
import { MatChipInputEvent } from '@angular/material/chips';
import { ITag } from '../models/ITag.model';
import { HttpClient } from '@angular/common/http';
import { environment } from './../../environments/environment';

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

  tags: ITag[] = [
    { name: 'Test' },
  ];

  constructor(private httpClient: HttpClient) { }

  public ngOnInit() {
    this.httpClient.get(`${environment.serverUrl}/tags`)
      .subscribe((value: Array<ITag>) => {
        this.tags = value;
      });
  }

  public add(event: MatChipInputEvent): void {
    const input = event.input;
    const value = event.value;
    if ((value || '').trim()) {
      this.tags.push({ name: value.trim() });
    }
    if (input) {
      input.value = '';
    }
  }

  public remove(tag: ITag): void {
    const index = this.tags.indexOf(tag);

    if (index >= 0) {
      this.tags.splice(index, 1);
    }
  }

}
