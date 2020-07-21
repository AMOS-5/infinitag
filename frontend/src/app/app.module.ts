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

import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatListModule } from '@angular/material/list';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatSelectModule } from '@angular/material/select';
import { MatMenuModule } from '@angular/material/menu';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { MatTreeModule } from '@angular/material/tree';
import { MatDialogModule } from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatTooltipModule } from '@angular/material/tooltip';
import { NgxDaterangepickerMd } from 'ngx-daterangepicker-material';

import { AppComponent } from './app.component';
import { DocumentViewTableComponent } from './documentview/document-view-table.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { DocumentationComponent } from './documentation/documentation.component';
import { KeywordsComponent } from './keywords/keywords.component';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { DragdropDirective } from '../directives/dragdrop.directive';
import { FileUploadComponent } from './file-upload/file-upload.component';
import { FileExistsDialogComponent } from '../dialogs/file-exists.component';
import { MatTabsModule} from '@angular/material/tabs';
import { FileUploadDialogComponent } from '../dialogs/file-upload.dialog.component';
import { TaggingComponent } from './tagging/tagging.component';
import { TaggingDialogComponent } from '../dialogs/tagging.dialog.component';
import { AutomatedTaggingParametersDialog } from '../dialogs/automated-tagging-parameters.component';
import { NaturalNumbersOnlyDirective } from '../directives/natural-numbers-only.directive';
import { DocumentOverviewComponent } from './document-overview/document-overview.component';
import { KWMNameDialog } from '../dialogs/keyword-input.dialog.component';

import * as echarts from 'echarts';
import { NgxEchartsModule } from 'ngx-echarts';


export function HttpLoaderFactory(httpClient: HttpClient) {
  return new TranslateHttpLoader(httpClient);
}

@NgModule({
  declarations: [
    AppComponent,
    DocumentViewTableComponent,
    FileUploadComponent,
    DashboardComponent,
    DocumentationComponent,
    KeywordsComponent,
    KWMNameDialog,
    DragdropDirective,
    FileExistsDialogComponent,
    FileUploadDialogComponent,
    TaggingComponent,
    TaggingDialogComponent,
    AutomatedTaggingParametersDialog,
    NaturalNumbersOnlyDirective,
    DocumentOverviewComponent
  ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        HttpClientModule,
        FormsModule,
        MatTableModule,
        MatSortModule,
        BrowserAnimationsModule,
        MatChipsModule,
        MatFormFieldModule,
        MatInputModule,
        MatIconModule,
        MatSnackBarModule,
        MatListModule,
        MatProgressBarModule,
        MatToolbarModule,
        MatButtonModule,
        MatGridListModule,
        MatCheckboxModule,
        MatSelectModule,
        MatMenuModule,
        MatButtonToggleModule,
        DragDropModule,
        MatTreeModule,
        MatExpansionModule,
        MatDialogModule,
        MatAutocompleteModule,
        MatPaginatorModule,
        MatTooltipModule,
        TranslateModule.forRoot({
            loader: {
                provide: TranslateLoader,
                useFactory: HttpLoaderFactory,
                deps: [HttpClient]
            }
        }),
        ReactiveFormsModule,
        MatProgressSpinnerModule,
        MatTabsModule,
        NgxEchartsModule.forRoot({
          echarts
        }),
        NgxDaterangepickerMd.forRoot()
    ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule { }
