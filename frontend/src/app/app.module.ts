import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import {HttpClientModule} from '@angular/common/http';
import {FormsModule} from '@angular/forms';
import {MatTableModule} from '@angular/material/table'; 


import { AppComponent } from './app.component';
import { DocumentViewTable } from './documentview/document-view-table';


@NgModule({
  declarations: [
    AppComponent,
    DocumentViewTable
  ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        HttpClientModule,
        FormsModule,
        MatTableModule
    ],
  providers: [],
  bootstrap: [AppComponent, DocumentViewTable]
})
export class AppModule { }
