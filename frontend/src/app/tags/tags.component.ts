import { Component, OnInit } from '@angular/core';
import { COMMA, ENTER, SPACE } from '@angular/cdk/keycodes';
import { MatChipInputEvent } from '@angular/material/chips';
import { ApiService } from '../services/api.service';
import { MatSnackBar } from '@angular/material/snack-bar';
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
  tags = [];
  readonly separatorKeysCodes: number[] = [ENTER, COMMA, SPACE];

  constructor(private api: ApiService, private snackBar: MatSnackBar) { }

  public ngOnInit() {
    this.api.getTags()
      .subscribe((data: []) => {
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
            this.snackBar.open(`${value} added into the database`, '', { duration: 3000 });
          });
      } else {
        this.snackBar.open(`${value} already present`, '', { duration: 3000 });
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
        console.log(res)
        this.snackBar.open(`${tag} deleted from the database`, '', { duration: 3000 });
      });
  }

}
