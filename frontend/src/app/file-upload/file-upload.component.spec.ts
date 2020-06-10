import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { FileUploadComponent } from './file-upload.component';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MatListModule } from '@angular/material/list';
import {TranslateLoader, TranslateModule, TranslateService} from '@ngx-translate/core';
import {HttpLoaderFactory} from '../app.module';
import {HttpClient} from '@angular/common/http';

describe('FileUploadComponent', () => {
  let component: FileUploadComponent;
  let fixture: ComponentFixture<FileUploadComponent>;
  let translate: TranslateService;

  const file1 = new File(['test1'], 'spec_test_file1.test', { type: 'text/plain' });
  const file2 = new File(['test2'], 'spec_test_file2.test', { type: 'text/plain' });


  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
        MatListModule,
        TranslateModule.forRoot({
          loader: {
            provide: TranslateLoader,
            useFactory: HttpLoaderFactory,
            deps: [HttpClient]
          }
        })
      ],
      declarations: [ FileUploadComponent ]
    })
    .compileComponents();
    translate = TestBed.get(TranslateService);
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FileUploadComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should add files to list', () => {
    const list = new DataTransfer();
    list.items.add(file1);
    list.items.add(file2);
    component.onSelectFile(list.files);

    expect(component.files.length).toEqual(2);
    expect(component.files[0]).toEqual({file: file1,
      status: 'request send',
      progress: 0,
      icon: 'schedule'});

  });
});
