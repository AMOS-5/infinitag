import { TestBed, async, ComponentFixture } from '@angular/core/testing';
import { DocumentViewTable } from './document-view-table';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MatSortable, MatSortModule, } from '@angular/material/sort';
import { MatTableModule } from '@angular/material/table';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

describe('DocumentViewTable', () => {
  let component: DocumentViewTable;
  let fixture: ComponentFixture<DocumentViewTable>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
        MatSortModule,
        MatTableModule,
        BrowserAnimationsModule,
      ],
      declarations: [DocumentViewTable]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DocumentViewTable);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('test received data', () => {
    //TODO extend testcase once real data is read
    expect(component.dataSource).toBeTruthy();
  });

  it('test sorting data', () => {
    //tests sorting functionality by comparing first and last row before and after sorting
    component.sort.sort(({ id: 'name', start: 'asc' }) as MatSortable);
    const dataLength = component.dataSource.data.length;
    let firstrow = component.dataSource.sortData[0];
    let lastrow = component.dataSource.sortData[dataLength - 1];
    component.sort.sort(({ id: 'name', start: 'asc' }) as MatSortable);
    expect(firstrow).toEqual(component.dataSource.sortData[dataLength - 1]);
    expect(lastrow).toEqual(component.dataSource.sortData[0]);
  });

});
