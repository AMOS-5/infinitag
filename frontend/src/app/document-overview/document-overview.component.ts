/**
 * @license
 * InfiniTag
 * Copyright (c) 2020 AMOS-5.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

import { Component, OnInit } from '@angular/core';
import { IDocument } from '../models/IDocument.model';
import { environment } from './../../environments/environment';
import { ApiService } from '../services/api.service';
import {TranslateService} from '@ngx-translate/core';
@Component({
  selector: 'app-document-overview',
  templateUrl: './document-overview.component.html',
  styleUrls: ['./document-overview.component.scss']
})

export class DocumentOverviewComponent implements OnInit {
  public title = 'infinitag';
  public serverUrl = environment.serverUrl;
  public backendStatus = `${this.serverUrl}/health`;
  public documentsUrl = `${this.serverUrl}/documents`;


  public serverStatus = 'DOWN';

  public documents: Array<IDocument> = [];
  public page;
  public num_per_page;
  public sort_field;
  public sort_order;
  public total_pages;
  public filterString = '';



  constructor(private api: ApiService, private translate: TranslateService) {}

  public ngOnInit(): void {
    this.api.getDocuments()
      .subscribe((value: any) => {
        console.log(value);
        this.documents = value.docs;
        this.page = value.page;
        this.num_per_page = value.num_per_page;
        this.sort_field = value.sort_field;
        this.sort_order = value.sort_order;
        this.total_pages = value.total_pages;
      });
  }
}
