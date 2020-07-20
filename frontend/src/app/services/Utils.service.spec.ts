import { TestBed } from '@angular/core/testing';

import { Utils } from './Utils.service';
import { HttpClientTestingModule } from '@angular/common/http/testing';

describe('Utils', () => {
  let service: Utils;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule
      ]
    });
    service = TestBed.inject(Utils);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
