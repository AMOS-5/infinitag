import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { HomeComponent } from './home.component';
import { MatSortModule, } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { DocumentViewTableComponent } from '../documentview/document-view-table.component';
import { IDocument } from '../models/IDocument.model';
import { concatMap } from 'rxjs/operators';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatInputModule } from '@angular/material/input';
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';

describe('HomeComponent', () => {
  let component: HomeComponent;
  let fixture: ComponentFixture<HomeComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
        MatSortModule,
        MatTableModule,
        BrowserAnimationsModule,
        MatInputModule,
        MatFormFieldModule,
        MatToolbarModule
      ],
      declarations: [HomeComponent, DocumentViewTableComponent],
      schemas: [
        CUSTOM_ELEMENTS_SCHEMA
      ]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(HomeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
