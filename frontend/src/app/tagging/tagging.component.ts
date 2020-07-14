import {
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChild
} from '@angular/core';
import { ITaggingMethod } from '../models/ITaggingMethod';
import { ApiService } from '../services/api.service';
import { FormBuilder, FormControl } from '@angular/forms';
import { IKeywordListEntry } from '../models/IKeywordListEntry.model';
import { ITaggingRequest } from '../models/ITaggingRequest.model';
import { IDocument } from '../models/IDocument.model';
import { MatAutocomplete, MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { MatChipInputEvent } from '@angular/material/chips';
import { Observable, of, throwError } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { MatSnackBar } from '@angular/material/snack-bar';
import { IKeyword } from '../models/IKeyword.model';
import { UploadService } from '../services/upload.service';
import { TaggingDialogComponent, TaggingDialogData } from '../../dialogs/tagging.dialog.component';
import { MatDialog } from '@angular/material/dialog';
import { Utils } from '../services/Utils.service';
import { AutomatedTaggingParametersDialog, DialogData } from '../../dialogs/automated-tagging-parameters.component';


@Component({
  selector: 'app-tagging',
  templateUrl: './tagging.component.html',
  styleUrls: ['./tagging.component.scss']
})
export class TaggingComponent implements OnInit {
  applyingTaggingMechanism = false;
  selectable = true;
  removable = true;
  keywordModels: any = [];
  kwmToAdd = [];
  bulkKwCtrl = new FormControl([]);
  separatorKeysCodes: number[] = [ENTER, COMMA];

  // list of all keywords (uncategorized + kwm)
  keywords: IKeywordListEntry[] = [];
  selectedKeywords: IKeywordListEntry[] = [];

  // list of keywords filtered and display in the drop down menu
  filteredBulkKeywords: Observable<IKeywordListEntry[]>;

  // list of keywords selected for applying/deleting
  selectedBulkKeywords: IKeywordListEntry[] = [];

  // kwm seclected from the drop down menu
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
    public dialog: MatDialog,
    private snackBar: MatSnackBar,
    private uploadService: UploadService,
    private utils: Utils) {
    this.taggingForm = this.formBuilder.group({
      taggingMethod: this.selectedTaggingMethod,
      keywordModel: undefined,
      documents: [],
      bulkKeywords: []
    });
  }

  public ngOnInit(): void {
    this.api.getKeywordListEntries()
      .subscribe((data: []) => {
        this.keywords = data;
        this.selectedKeywords = this.keywords;
        this.filteredBulkKeywords = this.bulkKwCtrl.valueChanges.pipe(
          startWith(''),
          map((selectedBulkKeyword: IKeywordListEntry | null) => {
            return selectedBulkKeyword ? this._filter(selectedBulkKeyword) : this.selectedKeywords.slice()
          })
        );
      })
    this.api.getKeywordModels()
      .subscribe((data: any) => {
        this.keywordModels = data;
      });
  }

  public openTaggingDialog(dialogData: TaggingDialogData): void {
    const dialogRef = this.dialog.open(TaggingDialogComponent, {
      width: '1200px',
      data: dialogData
    });

    dialogRef.afterClosed().subscribe((response: string) => {
      if (response === 'cancel') {
        this.api.cancelJob(dialogData.jobId)
          .subscribe((res: any) => {
            this.snackBar.open('Job cancelled', ``, { duration: 3000 });
          });
      }
      this.taggingApplied.emit();
    });
  }

  /**
   * @description
   * Adds all selected keywords and their parents to all selected documents.
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

  /**
   * @description
   * Removes all selected keywords from to all selected documents.
   * Parent keywords are not touched and only the keyword string matters; the
   * kwm of the keywords doesn't get compared.
   */
  public deleteBulkKeywords() {
    if (this.selectedDocuments.length === 0) {
      this.snackBar.open('no rows selected', ``, { duration: 3000 });
    }
    this.selectedBulkKeywords.forEach(keyword => {
      this.selectedDocuments.forEach(document => {
        const index = document.keywords.map(kw => kw.value).indexOf(keyword.id);
        if (index >= 0) {
          document.keywords.splice(index, 1);
        }

        this.uploadService.patchKeywords(document).subscribe(res => {
          this.keywordsApplied.emit();
        });
      });
    });
    this.selectedBulkKeywords = [];
  }

  public changeTaggingMethod(event: any) {
    this.selectedTaggingMethod = event.value;
  }

  public changeKWM(event: any) {
    this.selectedKeywordModel = event.value;
  }

  /**
   * Upon submitting the tagging mechanism, the method will be applied and the documents
   * will be fetched again to update the table
   */
  public onSubmit() {
    const jobId = this.utils.uuid4();
    const taggingData: ITaggingRequest = {
      taggingMethod: this.selectedTaggingMethod,
      documents: this.selectedDocuments,
      keywordModel: this.selectedKeywordModel,
      options: {},
      jobId
    };
    if (this.selectedTaggingMethod.name === 'Automated') {
      const dialogRef = this.dialog.open(AutomatedTaggingParametersDialog, {
        width: '300px',
        data: { computeOptimal: false, numClusters: 5, numKeywords: 5 }
      });

      dialogRef.afterClosed().subscribe((result: DialogData) => {
        if (result === undefined) { return; } // cancel was pressed

        result.numClusters = Number(result.numClusters);
        result.numKeywords = Number(result.numKeywords);

        if (result.numClusters === 0 || result.numKeywords === 0) { // happens if an empty string is inserted
          this.snackBar.open('invalid parameters', ``, { duration: 3000 });
          return;
        }

        taggingData.options = result;

        this.api.applyTaggingMethod(taggingData).subscribe(
          () => {
            this.applyingTaggingMechanism = false;
          });
        this.openMonitoring(jobId);
      });
    } else {
      this.api.applyTaggingMethod(taggingData).subscribe(() => {
        this.applyingTaggingMechanism = false;
      });
      this.openMonitoring(jobId);
    }

  }

  public openMonitoring(jobId: string) {
    const taggingDialogData: TaggingDialogData = {
      status: 'Documents are being tagged...',
      progress: 0,
      jobId,
      timeRemaining: -1
    };
    this.openTaggingDialog(taggingDialogData);
    this.applyingTaggingMechanism = true;

    this.monitorJobProgress(taggingDialogData)
      .then(() => {
        this.snackBar.open(`Finished tagging with Job ID: ${taggingDialogData.jobId}`, '', { duration: 3000 });
      }
    );
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
      const kw: IKeywordListEntry = { id: value, kwm: null, parents: [] };
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
   * to update the document. If angular compile switch to browser the request is succesfull the datasource gets
   * updated.
   */
  public applyKeyword(doc: IDocument, keyword: IKeywordListEntry) {
    let toAdd = [keyword.id];
    toAdd = toAdd.concat(keyword.parents);
    for (let i = 0; i < toAdd.length; i++) {
      const kw: IKeyword = { value: toAdd[i], type: 'MANUAL' };
      this.addKeywordToDoc(doc, kw).subscribe(
        res => {
          doc = res;
        },
        err => this.snackBar.open(err, ``, { duration: 3000 })
      );
    }

    this.uploadService.patchKeywords(doc).subscribe(() => {
      this.keywordsApplied.emit();
    });
  }

  public async monitorJobProgress(taggingDialogData: TaggingDialogData) {
    const jobId = taggingDialogData.jobId;

    while (taggingDialogData.status.toLowerCase() !== 'finished') {
      this.api.getTaggingJobStatus(jobId)
        .subscribe((response: any) => {
          taggingDialogData.progress = response.progress;
          taggingDialogData.status = response.message;
          taggingDialogData.timeRemaining = response.timeRemaining;
        });
      await this.delay(2000);
    }
  }

  private delay(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
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
    if (typeof (value) === 'string') {
      filterValue = value.toLowerCase();
    } else {
      filterValue = value.id.toLowerCase();
    }
    return this.selectedKeywords.filter(keyword => keyword.id.toLowerCase().indexOf(filterValue) === 0);
  }

}
