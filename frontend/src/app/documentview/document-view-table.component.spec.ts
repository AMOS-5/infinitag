import { TestBed, async, ComponentFixture } from '@angular/core/testing';
import { DocumentViewTableComponent } from './document-view-table.component';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MatSortable, MatSortModule, } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { IDocument } from '../models/IDocument.model';

describe('DocumentViewTable', () => {
  let component: DocumentViewTableComponent;
  let fixture: ComponentFixture<DocumentViewTableComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
        MatSortModule,
        MatTableModule,
        BrowserAnimationsModule,
      ],
      declarations: [DocumentViewTableComponent]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DocumentViewTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('test received data', () => {
    expect(component.dataSource).toBeTruthy();
  });

  it('test sorting data', () => {
    // tests sorting functionality by comparing first and last row before and after sorting
    component.sort.sort(({ id: 'name', start: 'asc' }) as MatSortable);
    const dataLength = component.dataSource.data.length;
    const firstrow = component.dataSource.sortData[0];
    const lastrow = component.dataSource.sortData[dataLength - 1];
    component.sort.sort(({ id: 'name', start: 'asc' }) as MatSortable);
    expect(firstrow).toEqual(component.dataSource.sortData[dataLength - 1]);
    expect(lastrow).toEqual(component.dataSource.sortData[0]);
  });

  it('Should filter documents based on filter string', () => {
    const testDocuments: Array<IDocument> = [
      {
        size: 1,
        language: 'en',
        creation_date: new Date(),
        title: 'Test 1',
        id: '/path',
        tags: ['Tag 1', 'Test Document'],
        type: 'pdf',
        content: ''
      },
      {
        size: 3,
        language: 'de',
        creation_date: new Date(),
        title: 'Test 2',
        id: '/path',
        tags: ['Tag 2', 'Test Document'],
        type: 'eml',
        content: ''
      }
    ];

    component.documents = testDocuments;
    component.ngOnInit();
    expect(component.documents).toEqual(testDocuments);
    component.dataSource.filter = 'pdf';
    expect(component.dataSource.filteredData.length).toEqual(1);
  });

});
