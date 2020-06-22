import { TestBed } from '@angular/core/testing';
import { UploadService } from './upload.service';
import { HttpClientTestingModule, HttpTestingController, TestRequest } from '@angular/common/http/testing';
import { HttpEventType, HttpEvent } from '@angular/common/http';
import { environment } from './../../environments/environment';
import { skipWhile } from 'rxjs/operators';
import { IDocument } from '../models/IDocument.model';
import {IFile} from "../models/IFile.model";


describe('UploadService', async () => {
  let service: UploadService;
  let http: HttpTestingController;
  const fileData = new File(['test'], 'spec_test_file.test', { type: 'text/plain' });
  const file: IFile = {
    fid: '',
    file: fileData,
    status: '',
    icon: '',
    progress: 0
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule,
      ]
    });
    service = TestBed.inject(UploadService);
    http = TestBed.get(HttpTestingController);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should send correct POST request', () => {
    let attemptedEvent;
    service.postFile(file).subscribe(event => {
      attemptedEvent = event;

    });

    const req = http.expectOne(`${environment.serverUrl}/upload`);
    req.flush(attemptedEvent);

    // console.log(req)
    // console.log(attemptedEvent)

    expect(req.request.method).toEqual('POST');
    expect(attemptedEvent.status).toEqual(200);
  });

  it('should send correct PATCH request', () => {
    let attemptedEvent;

    const iDoc: IDocument = {
      content: 'abc',
      creation_date: new Date(),
      id: 'test/test_file.pdf',
      language: 'eng',
      size: 33,
      keywords: [{value: 'key1', type: 'MANUAL'}, {value: 'key2', type: 'MANUAL'}, {value: 'key3', type: 'MANUAL'}],
      title: 'test_file',
      type: 'pdf',
    };
    service.patchKeywords(iDoc).subscribe(event => {
      attemptedEvent = event;
    });

    const req = http.expectOne(`${environment.serverUrl}/changekeywords`);
    req.flush(iDoc);
    expect(req.request.method).toEqual('PATCH');
  });
});
