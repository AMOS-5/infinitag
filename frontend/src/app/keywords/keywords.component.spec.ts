import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { KeywordsComponent, ItemFlatNode } from './keywords.component';
import { MatDialogModule } from '@angular/material/dialog';
import { MatTreeModule } from '@angular/material/tree';
import {MatListModule} from '@angular/material/list';

describe('KeywordsComponent', () => {
  let component: KeywordsComponent;
  let fixture: ComponentFixture<KeywordsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ KeywordsComponent ],
      imports: [
        HttpClientTestingModule,
        MatSnackBarModule,
        MatGridListModule,
        MatIconModule,
        DragDropModule,
        MatFormFieldModule,
        FormsModule,
        MatInputModule,
        BrowserAnimationsModule,
        MatDialogModule,
        MatTreeModule,
        MatListModule,
      ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(KeywordsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('test should receive dimension data', () => {
    expect(component.uncatDimensions).toBeTruthy();
  });

  it('test should receive keyword data', () => {
    expect(component.uncatKeywords).toBeTruthy();
  });

  it('test should receive keywordmodel data', () => {
    expect(component.keywordModels).toBeTruthy();
  });

  it('test should add item in keywordmodel', () => {
    var node = new ItemFlatNode();
    node.item = "test";
    node.level = 0;
    node.expandable = true;
    component.dragNode = node;
    component.handleDrop("", node)
    expect(component.dataSource.data).toBeTruthy(); //todo
  });
});
