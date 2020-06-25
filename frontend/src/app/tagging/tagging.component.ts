import {
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnChanges,
  OnInit,
  Output,
  SimpleChanges,
  ViewChild
} from '@angular/core';
import {ITaggingMethod} from '../models/ITaggingMethod';
import {ApiService} from '../services/api.service';
import {FormBuilder, FormControl} from '@angular/forms';
import {IKeywordListEntry} from '../models/IKeywordListEntry.model';
import {ITaggingRequest} from '../models/ITaggingRequest.model';
import {IDocument} from '../models/IDocument.model';
import {SelectionModel} from '@angular/cdk/collections';
import {MatAutocomplete, MatAutocompleteSelectedEvent} from '@angular/material/autocomplete';
import {MatChipInputEvent} from '@angular/material/chips';
import {Observable, of, throwError} from 'rxjs';
import {map, startWith} from 'rxjs/operators';
import {COMMA, ENTER} from '@angular/cdk/keycodes';
import {MatSnackBar} from '@angular/material/snack-bar';
import {IKeyword} from '../models/IKeyword.model';
import {UploadService} from '../services/upload.service';


@Component({
  selector: 'app-tagging',
  templateUrl: './tagging.component.html',
  styleUrls: ['./tagging.component.scss']
})
export class TaggingComponent implements OnInit, OnChanges {
  keywords: IKeywordListEntry[] = [];
  selectedKeywords: IKeywordListEntry[] = [];
  applyingTaggingMechanism = false;
  selectable = true;
  removable = true;
  keywordModels: any = [];
  kwmToAdd = [];
  bulkKwCtrl = new FormControl([]);
  separatorKeysCodes: number[] = [ENTER, COMMA];
  filteredBulkKeywords: Observable<IKeywordListEntry[]>;
  selectedBulkKeywords: IKeywordListEntry[] = [];
  selectedKeywordModel: any;

  @Input() editing = false;
  @Input() selectedDocuments = [];

  @Output() taggingApplied = new EventEmitter();
  @Output() keywordsApplied = new EventEmitter();

  @ViewChild('bulkKWInput') KWInput: ElementRef<HTMLInputElement>;
  @ViewChild('auto') matAutocomplete: MatAutocomplete;

  public taggingMethods: Array<ITaggingMethod> = [
    {
      name: 'Keyword Model',
      type: 'KWM'
    },
    {
      name: 'Automated',
      type: 'ML'
    }
  ];

  public taggingForm;

  public selectedTaggingMethod = this.taggingMethods[0];
  constructor(private api: ApiService,
              private formBuilder: FormBuilder,
              private snackBar: MatSnackBar,
              private uploadService: UploadService) {
    this.taggingForm = this.formBuilder.group({
      taggingMethod: this.selectedTaggingMethod,
      keywordModel: undefined,
      documents: [],
      bulkKeywords: []
    });
    // @ts-ignore
    this.filteredBulkKeywords = this.bulkKwCtrl.valueChanges.pipe(
      startWith(null),
      map((selectedBulkKeyword: IKeywordListEntry | null) =>  {
        selectedBulkKeyword ? this._filter(selectedBulkKeyword) : this.selectedKeywords.slice();
      }));
  }

  public ngOnInit(): void {
    this.api.getKeywordListEntries()
          .subscribe((data: []) => {
            this.keywords = data;
            this.selectedKeywords = this.keywords;
          });
    this.api.getKeywordModels()
          .subscribe((data: any) => {
            this.keywordModels = data;
          });
  }

  /**
   * @description
   * Adds a keyword and its parents to all selected documents.
   */
  public applyBulkKeywords() {
    if (this.selectedDocuments.length === 0) {
      this.snackBar.open('no rows selected', ``, { duration: 3000 });
    }
    this.selectedBulkKeywords.forEach(keyword => {
      if (!this.selectedKeywords.includes(keyword)) {
        this.api.addUncategorizedKeyword(keyword.id).subscribe(() => {

        });
      }
      this.selectedDocuments.forEach(doc => {
        this.applyKeyword(doc, keyword);
      });
    });
    this.selectedBulkKeywords = [];
  }

  public changeTaggingMethod(event: any) {
    this.selectedTaggingMethod = event.value;
    console.log(this.selectedTaggingMethod)
  }

  public changeKWM(event: any) {
    this.selectedKeywordModel = event.value;
    console.log(this.selectedKeywordModel);
  }

  /**
   * Upon submitting the tagging mechanism, the method will be applied and the documents
   * will be fetched again to update the table
   */
  public onSubmit() {
    this.applyingTaggingMechanism = true;
    const taggingData: ITaggingRequest = {
      taggingMethod: this.selectedTaggingMethod,
      documents: this.selectedDocuments,
      keywordModel: this.selectedKeywordModel
    };
    this.api.applyTaggingMethod(taggingData).subscribe( (response: any) => {
      if (response.status === 200) {
        this.taggingApplied.emit(true);
      }
      this.applyingTaggingMechanism = false;
    });
  }

  public selected(event: MatAutocompleteSelectedEvent): void {
    this.selectedBulkKeywords.push(event.option.value);
    this.KWInput.nativeElement.value = '';
    this.bulkKwCtrl.setValue(null);
  }


  public add(event: MatChipInputEvent): void {
    const input = event.input;
    const value = event.value;

    if ((value || '').trim()) {
      const kw: IKeywordListEntry = {id: value, kwm: null, parents: []};
      this.selectedBulkKeywords.push(kw);
    }

    // Reset the input value
    if (input) {
      input.value = '';
    }
    this.bulkKwCtrl.setValue(null);
  }

  public remove(keyword: IKeywordListEntry): void {
    const index = this.selectedBulkKeywords.indexOf(keyword);

    if (index >= 0) {
      this.selectedBulkKeywords.splice(index, 1);
    }
  }

  /**
   * @description
   * Adds a keyword and all its parents to a document, then sends a PATCH request to the backend
   * to update the document. If angular compile switch to browserthe request is succesfull the datasource gets
   * updated.
   */
  public applyKeyword(doc: IDocument, keyword: IKeywordListEntry) {
    let toAdd = [keyword.id];
    toAdd = toAdd.concat(keyword.parents);
    for (let i = 0; i < toAdd.length; i++) {
      const kw: IKeyword = {value: toAdd[i], type: 'MANUAL'};
      this.addKeywordToDoc(doc, kw).subscribe(
        res => {
          doc = res;
        },
        err => this.snackBar.open(err, ``, {duration: 3000})
      );
    }

    this.uploadService.patchKeywords(doc).subscribe(() => {
      this.keywordsApplied.emit();
    });
  }

   /**
    * @description
    * Adds a new keyword to an IDocument object. Thorws an error if the keyword
    * is already added to the document
    */
  private addKeywordToDoc = (iDoc: IDocument, keyword: IKeyword): Observable<IDocument> => {
    if (iDoc.keywords.filter(kw => kw.value === keyword.value).length === 0) {
      iDoc.keywords.push(keyword);
      iDoc.keywords.sort((a, b) => a.value.localeCompare(b.value));
      return of(iDoc);
    } else {
      return throwError('Keyword ' + keyword.value + ' already added to ' + iDoc.title);
    }
  }


  private _filter(value): IKeywordListEntry[] {
    let filterValue;
    if (typeof(value) === 'string') {
      filterValue = value.toLowerCase();
    } else {
      filterValue = value.id.toLowerCase();
    }
    return this.selectedKeywords.filter(keyword => keyword.id.toLowerCase().indexOf(filterValue) === 0);
  }

  public ngOnChanges(changes: SimpleChanges): void {
    console.log(changes);
  }

}
