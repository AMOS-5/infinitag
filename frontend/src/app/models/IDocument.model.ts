import { Time } from '@angular/common';

export interface IDocument {
  content: string;
  creation_date: Date;
  id: string;
  language: string;
  size: number;
  keywords: string[];
  title: string;
  type: string;
}
