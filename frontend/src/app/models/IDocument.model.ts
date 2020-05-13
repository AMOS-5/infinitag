export interface IDocument {
  name: string;
  path: string;
  type: string;
  lang: string;
  size: number;
  createdAt: Date;
  tags: string[];
}
