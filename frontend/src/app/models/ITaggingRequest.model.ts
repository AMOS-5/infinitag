import {ITaggingMethod} from './ITaggingMethod';
import {IKeyWordModel} from './IKeyWordModel.model';
import {IDocument} from './IDocument.model';

export interface ITaggingRequest {
  taggingMethod: ITaggingMethod;
  keywordModel: IKeyWordModel | undefined;
  documents: Array<IDocument>;
}
