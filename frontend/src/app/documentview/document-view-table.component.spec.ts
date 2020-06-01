import { TestBed, async, ComponentFixture } from '@angular/core/testing';
import { DocumentViewTableComponent } from './document-view-table.component';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MatSortable, MatSortModule } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
import { MatMenuModule } from '@angular/material/menu';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { IDocument } from '../models/IDocument.model';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatButtonToggleModule } from '@angular/material/button-toggle';


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
        MatMenuModule,
        FormsModule,
        MatFormFieldModule,
        MatInputModule,
        MatIconModule,
        ReactiveFormsModule,
        MatSnackBarModule,
        MatCheckboxModule,
        MatButtonToggleModule,
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
        keywords: ['Key 1', 'Test Document'],
        type: 'pdf',
        content: ''
      },
      {
        size: 3,
        language: 'de',
        creation_date: new Date(),
        title: 'Test 2',
        id: '/path',
        keywords: ['Key 2', 'Test Document'],
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

  it('should correctly add keywords to doc', () => {
    let doc = {
      size: 1,
      language: 'en',
      creation_date: new Date(),
      title: 'Test 1',
      id: '/path',
      keywords: ['b'],
      type: 'pdf',
      content: ''
    };
    expect(doc.keywords.length).toEqual(1);

    // @ts-ignore
    component.addKeywordToDoc(doc, "b").subscribe(res => {
      expect(res.keywords.length).toEqual(1);
    },
    err => {
      expect(err).toEqual("Keyword already added to Test 1");
    });

    // @ts-ignore
    component.addKeywordToDoc(doc, "a").subscribe(res => {
      expect(res.keywords.length).toEqual(2);
      expect(res.keywords).toEqual(["a", "b"]);
    });

  });

});
