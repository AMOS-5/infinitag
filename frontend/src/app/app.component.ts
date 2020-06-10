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

import {Component, OnInit} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../environments/environment';
import {TranslateService} from '@ngx-translate/core';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  public title = 'infinitag';
  public serverUrl = environment.serverUrl;
  public backendStatus = `${this.serverUrl}/health`;
  public serverStatus = 'DOWN';

  public iconPath = 'assets/img/InfiniTag1.png';
  public availableLanguages = ['en', 'de'];
  public selectedLanguage = 'en';


  constructor(
    private httpClient: HttpClient,
    public translate: TranslateService) {
    translate.addLangs(this.availableLanguages);
    translate.setDefaultLang(this.selectedLanguage);

    const browserLang = translate.getBrowserLang();
    translate.use(browserLang.match(/en|de/) ? browserLang : 'en');
    if ( this.availableLanguages.indexOf(browserLang) !== -1)  {
      this.selectedLanguage = browserLang;
    }
  }
  public ngOnInit(): void {
    this.httpClient.get(this.backendStatus)
      .subscribe((value: { status: string }) => {
        this.serverStatus = value.status;
      });
  }

  public changeLanguage(event: any) {
    this.translate.use(event.value);
  }
}
