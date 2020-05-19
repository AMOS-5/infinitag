import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { MatChipInputEvent } from '@angular/material/chips';
import { TagsComponent } from './tags.component';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBarModule } from '@angular/material/snack-bar';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

describe('TagsComponent', () => {
  let component: TagsComponent;
  let fixture: ComponentFixture<TagsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [TagsComponent],
      imports: [
        HttpClientTestingModule,
        MatFormFieldModule,
        MatInputModule,
        MatIconModule,
        BrowserAnimationsModule,
        MatChipsModule,
        MatSnackBarModule
      ],
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TagsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('shound create tags', () => {
    expect(component.tags).toBeTruthy();
  });

  it('should add new tag', () => {
    const hostElement = fixture.nativeElement;
    const tagInput: MatChipInputEvent = hostElement.querySelector('input');
    tagInput.value = 'test';
    component.add(tagInput);
    const lastTag = component.tags[component.tags.length - 1];
    expect(lastTag).toEqual(tagInput.value);
  });

  it('should delete tag', () => {
    if (component.tags && component.tags.length) {
      component.tags.splice(component.tags.length - 1, 1);
      console.log(component.tags);
      if (component.tags && component.tags.length) {
        expect(component.tags.length).toEqual(component.tags.length - 2);
      } else {
        expect(component.tags).toBeTruthy();
      }
    } else {
      expect(component.tags).toBeTruthy();
    }
  });
});
