import { Component, OnInit, Injectable, ViewChild, ElementRef } from '@angular/core';
import { CdkDragDrop, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService } from '../services/api.service';
import {FlatTreeControl} from '@angular/cdk/tree';
import {MatTreeFlatDataSource, MatTreeFlattener} from '@angular/material/tree';
import { BehaviorSubject } from 'rxjs';

/**
 * Node for item
 */
export class ItemNode {
  children: ItemNode[];
  item: string;
}

/** Flatitem node with expandable and level information */
export class ItemFlatNode {
  item: string;
  level: number;
  expandable: boolean;
}

/**
 * The Json object for list data.
 */
let TREE_DATA: any = [];

/**
 * Currently selected tree data.
 */
let selectedKwm: string;
/**
 * Checklist database, it can build a tree structured Json object.
 * Each node in Json object represents a item or a category.
 * If a node is a category, it has children items and new items can be added under the category.
 */
@Injectable()
export class ChecklistDatabase {
  static data(): any {
    throw new Error("Method not implemented.");
  }
  dataChange = new BehaviorSubject<ItemNode[]>([]);

  get data(): ItemNode[] { return this.dataChange.value; }

  constructor(private api: ApiService) {
    this.initialize();
  }

  initialize() {
    //Build the tree nodes from Json object. The result is a list of `ItemNode` with nested
    //    file node as children.
    this.api.getUncategorizedKeywords()
    .subscribe((data: []) => {

      for (var i = 0 ; i <= data.length; i++){
        let obj:any = new Object();
        obj[data[i]] = null;
        TREE_DATA[i] = this.buildFileTree( obj , 0);
      }

      // Notify the change.
      this.dataChange.next(TREE_DATA[0])
    });
  }

  /**
   * Build the file structure tree. The `value` is the Json object, or a sub-tree of a Json object.
   * The return value is the list of `ItemNode`.
   */
  buildFileTree(obj: object, level: number): ItemNode[] {
    return Object.keys(obj).reduce<ItemNode[]>((accumulator, key) => {
      const value = obj[key];
      const node = new ItemNode();
      node.item = key;

      if (value != null) {
        if (typeof value === 'object') {
          node.children = this.buildFileTree(value, level + 1);
        } else {
          node.item = value;
        }
      }

      return accumulator.concat(node);
    }, []);
  }

  /** Add an item to list */
  insertItem(parent: ItemNode, name: string): ItemNode {
    if (!parent.children) {
      parent.children = [];
    }
    const newItem = { item: name } as ItemNode;
    parent.children.push(newItem);
    this.dataChange.next(this.data);
    return newItem;
  }

  insertItemAbove(node: ItemNode, name: string): ItemNode {
    const parentNode = this.getParentFromNodes(node);
    const newItem = { item: name } as ItemNode;
    if (parentNode != null) {
      parentNode.children.splice(parentNode.children.indexOf(node), 0, newItem);
    } else {
      this.data.splice(this.data.indexOf(node), 0, newItem);
    }
    this.dataChange.next(this.data);
    return newItem;
  }

  insertItemBelow(node: ItemNode, name: string): ItemNode {
    const parentNode = this.getParentFromNodes(node);
    const newItem = { item: name } as ItemNode;
    if (parentNode != null) {
      parentNode.children.splice(parentNode.children.indexOf(node) + 1, 0, newItem);
    } else {
      this.data.splice(this.data.indexOf(node) + 1, 0, newItem);
    }
    this.dataChange.next(this.data);
    return newItem;
  }

  getParentFromNodes(node: ItemNode): ItemNode {
    for (let i = 0; i < this.data.length; ++i) {
      const currentRoot = this.data[i];
      const parent = this.getParent(currentRoot, node);
      if (parent != null) {
        return parent;
      }
    }
    return null;
  }

  getParent(currentRoot: ItemNode, node: ItemNode): ItemNode {
    if (currentRoot.children && currentRoot.children.length > 0) {
      for (let i = 0; i < currentRoot.children.length; ++i) {
        const child = currentRoot.children[i];
        if (child === node) {
          return currentRoot;
        } else if (child.children && child.children.length > 0) {
          const parent = this.getParent(child, node);
          if (parent != null) {
            return parent;
          }
        }
      }
    }
    return null;
  }

  updateItem(node: ItemNode, name: string) {
    node.item = name;
    this.dataChange.next(this.data);
  }

  deleteItem(node: ItemNode) {
    this.deleteNode(this.data, node);
    this.dataChange.next(this.data);
  }

  copyPasteItem(from: ItemNode, to: ItemNode, listItem?: ItemFlatNode): ItemNode {
    let newItem;

    if(!from) {
      newItem = this.insertItem(to, listItem.item);
    } else {
      newItem = this.insertItem(to, from.item);
    }

    if (from && from.children) {
      from.children.forEach(child => {
        this.copyPasteItem(child, newItem);
      });
    }
    return newItem;
  }

  copyPasteItemAbove(from: ItemNode, to: ItemNode, listItem?: ItemFlatNode): ItemNode {
    let newItem;

    if(!from) {
      newItem = this.insertItemAbove(to, listItem.item);
    } else {
      newItem = this.insertItemAbove(to, from.item);
    }
    if (from && from.children) {
      from.children.forEach(child => {
        this.copyPasteItem(child, newItem);
      });
    }
    return newItem;
  }

  copyPasteItemBelow(from: ItemNode, to: ItemNode, listItem?: ItemFlatNode): ItemNode {

    let newItem;
    if(!from) {
      newItem = this.insertItemBelow(to, listItem.item);
    } else {
      newItem = this.insertItemBelow(to, from.item);
    }

    if (from && from.children) {
      from.children.forEach(child => {
        this.copyPasteItem(child, newItem);
      });
    }
    return newItem;
  }

  deleteNode(nodes: ItemNode[], nodeToDelete: ItemNode) {
    const index = nodes.indexOf(nodeToDelete, 0);
    if (index > -1) {
      nodes.splice(index, 1);
    } else {
      nodes.forEach(node => {
        if (node.children && node.children.length > 0) {
          this.deleteNode(node.children, nodeToDelete);
        }
      });
    }
  }
}

@Component({
  selector: 'app-keywords',
  templateUrl: './keywords.component.html',
  styleUrls: ['./keywords.component.scss'],
  providers: [ChecklistDatabase]
})
export class KeywordsComponent implements OnInit {


  newDimension: string;
  newKeyword: string;
  isNewItem:boolean = false;
  newItem:any;
  uncatDimensions = []
  uncatKeywords = []
  keywords = []


  /** Map from flat node to nested node. This helps us finding the nested node to be modified */
  flatNodeMap = new Map<ItemFlatNode, ItemNode>();

  /** Map from nested node to flattened node. This helps us to keep the same object for selection */
  nestedNodeMap = new Map<ItemNode, ItemFlatNode>();

  /** A selected parent node to be inserted */
  selectedParent: ItemFlatNode | null = null;

  /** The new item's name */
  newItemName = '';

  treeControl: FlatTreeControl<ItemFlatNode>;

  treeFlattener: MatTreeFlattener<ItemNode, ItemFlatNode>;

  dataSource: MatTreeFlatDataSource<ItemNode, ItemFlatNode>;


  /* Drag and drop */
  dragNode: any;
  dragNodeExpandOverWaitTimeMs = 300;
  dragNodeExpandOverNode: any;
  dragNodeExpandOverTime: number;
  dragNodeExpandOverArea: string;
  @ViewChild('emptyItem') emptyItem: ElementRef;

  constructor(private api: ApiService, private snackBar: MatSnackBar, private database: ChecklistDatabase) {
    this.treeFlattener = new MatTreeFlattener(this.transformer, this.getLevel, this.isExpandable, this.getChildren);
    this.treeControl = new FlatTreeControl<ItemFlatNode>(this.getLevel, this.isExpandable);
    this.dataSource = new MatTreeFlatDataSource(this.treeControl, this.treeFlattener);

    database.dataChange.subscribe(data => {
      this.dataSource.data = [];
      this.dataSource.data = data;
    });
   }

  getLevel = (node: ItemFlatNode) => node.level;

  isExpandable = (node: ItemFlatNode) => node.expandable;

  getChildren = (node: ItemNode): ItemNode[] => node.children;

  hasChild = (_: number, _nodeData: ItemFlatNode) => _nodeData.expandable;

  hasNoContent = (_: number, _nodeData: ItemFlatNode) => _nodeData.item === '';

  /**
   * Transformer to convert nested node to flat node. Record the nodes in maps for later use.
   */
  transformer = (node: ItemNode, level: number) => {
    const existingNode = this.nestedNodeMap.get(node);
    const flatNode = existingNode && existingNode.item === node.item
      ? existingNode
      : new ItemFlatNode();
    flatNode.item = node.item;
    flatNode.level = level;
    flatNode.expandable = (node.children && node.children.length > 0);
    this.flatNodeMap.set(flatNode, node);
    this.nestedNodeMap.set(node, flatNode);
    return flatNode;
  }

  ngOnInit(): void {
    this.api.getUncategorizedKeywords()
    .subscribe((data: []) => {
      this.keywords = data;
    });
    this.api.getUncategorizedDimensions()
      .subscribe((data: []) => {
        this.uncatDimensions = data;
      });
    this.api.getUncategorizedKeywords()
      .subscribe((data: []) => {
        this.uncatKeywords = data;
      });
  }

  dropDim(event: CdkDragDrop<string[]>) {
    moveItemInArray(this.uncatDimensions, event.previousIndex, event.currentIndex);
  }

  dropKey(event: CdkDragDrop<string[]>) {
    moveItemInArray(this.uncatKeywords, event.previousIndex, event.currentIndex);
  }

  /**
  * @description
  * Gets called when the enter key is pressed while the uncategorized dimension
  * input field is in focus. The string gets read from the input, formatted
  * and added to the list as well as send to the backend
  */
  onDimEnter() {
    const dimFormatted = this.newDimension.trim().toLowerCase();
    if(dimFormatted !== "") {
      if(!this.isDuplicate(this.uncatDimensions, dimFormatted)) {
        this.api.addUncategorizedDimension(dimFormatted)
          .subscribe(res => {
            this.uncatDimensions.push(dimFormatted)
            this.snackBar.open(`${dimFormatted} added into the database`, '', { duration: 3000 });
          });
      } else {
        this.snackBar.open(`${dimFormatted} already present`, '', { duration: 3000 });
      }
    }
    this.newDimension="";
  }

  /**
  * @description
  * Gets called when the enter key is pressed while the uncategorized keyword
  * input field is in focus. The string gets read from the input, formatted
  * and added to the list as well as send to the backend
  */
  onKeyEnter() {
    const keyFormatted = this.newKeyword.trim().toLowerCase();
    if(keyFormatted !== "") {
      if(!this.isDuplicate(this.uncatKeywords, keyFormatted)) {
        this.api.addUncategorizedKeyword(keyFormatted)
          .subscribe(res => {
            this.uncatKeywords.push(keyFormatted)
            this.snackBar.open(`${keyFormatted} added into the database`, '', { duration: 3000 });
          });
      } else {
        this.snackBar.open(`${keyFormatted} already present`, '', { duration: 3000 });
      }
    }
    this.newKeyword="";
  }

  /**
  * @description
  * Checks if a value appears in an array
  * @param array to be checked
  * @param value to be checked
  * @returns true if the value was found, false otherwise
  */
  private isDuplicate(arr, value) {
    const index = arr.findIndex((elem) => elem === value);
    if (index === -1) {
      return false;
    }
    return true;
  }

  /**
  * @description
  * Sends a DELETE request to the backend. If it succedes the dimension is
  * removed from the list
  * @param {string} dimension to be removed
  */
  public deleteDimension(dimension: string) {
    const index = this.uncatDimensions.indexOf(dimension);

    if (index >= 0) {
      this.api.removeUncategorizedDimension(dimension)
      .subscribe(res => {
        this.uncatDimensions.splice(index, 1);
        this.snackBar.open(`${dimension} deleted from the database`, '', { duration: 3000 });
      });
    }
  }

  /**
  * @description
  * Sends a DELETE request to the backend. If it succedes the keyword is
  * removed from the list
  * @param {string} keyword to be removed
  */
  public deleteKeyword(keyword: string) {
    const index = this.uncatKeywords.indexOf(keyword);

    if (index >= 0) {
      this.api.removeUncategorizedKeyword(keyword)
      .subscribe(res => {
        this.uncatKeywords.splice(index, 1);
        this.snackBar.open(`${keyword} deleted from the database`, '', { duration: 3000 });
      });
    }
  }

  drop(event: CdkDragDrop<string[]>) {
    if (event.previousContainer === event.container) {
      moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
    } else {
      transferArrayItem(event.previousContainer.data,
                        event.container.data,
                        event.previousIndex,
                        event.currentIndex);
    }
  }

  /** Select the category so we can insert the new item. */
  addNewItem(node: ItemFlatNode) {
    const parentNode = this.flatNodeMap.get(node);
    this.database.insertItem(parentNode, '');
    this.treeControl.expand(node);
  }

  /** Save the node to database */
  saveNode(node: ItemFlatNode, itemValue: string) {
    const nestedNode = this.flatNodeMap.get(node);
    this.database.updateItem(nestedNode, itemValue);
  }

  handleDragStart(event, node, newItem) {
    if(newItem) {
      this.dragNode = new ItemFlatNode;
      this.dragNode.item = node;
      this.isNewItem = true;
      this.newItem = this.dragNode;
    } else {
      this.dragNode = node;
    }
    // Required by Firefox (https://stackoverflow.com/questions/19055264/why-doesnt-html5-drag-and-drop-work-in-firefox)
    event.dataTransfer.setData('foo', 'bar');
    event.dataTransfer.setDragImage(this.emptyItem.nativeElement, 0, 0);
    this.treeControl.collapse(node);
  }

  handleDragOver(event, node) {
    event.preventDefault();

    // Handle node expand
    if (node === this.dragNodeExpandOverNode) {
      if (this.dragNode !== node && !this.treeControl.isExpanded(node)) {
        if ((new Date().getTime() - this.dragNodeExpandOverTime) > this.dragNodeExpandOverWaitTimeMs) {
          this.treeControl.expand(node);
        }
      }
    } else {
      this.dragNodeExpandOverNode = node;
      this.dragNodeExpandOverTime = new Date().getTime();
    }

    // Handle drag area
    const percentageX = event.offsetX / event.target.clientWidth;
    const percentageY = event.offsetY / event.target.clientHeight;
    if (percentageY < 0.25) {
      this.dragNodeExpandOverArea = 'above';
    } else if (percentageY > 0.75) {
      this.dragNodeExpandOverArea = 'below';
    } else {
      this.dragNodeExpandOverArea = 'center';
    }
  }

  handleDrop(event, node) {
    if (node !== this.dragNode) {
      let newItem: ItemNode;
      if (this.dragNodeExpandOverArea === 'above') {
        newItem = this.database.copyPasteItemAbove(this.flatNodeMap.get(this.dragNode), this.flatNodeMap.get(node), this.newItem);
      } else if (this.dragNodeExpandOverArea === 'below') {
        newItem = this.database.copyPasteItemBelow(this.flatNodeMap.get(this.dragNode), this.flatNodeMap.get(node), this.newItem);
      } else {
        newItem = this.database.copyPasteItem(this.flatNodeMap.get(this.dragNode), this.flatNodeMap.get(node), this.newItem);
      }
      this.database.deleteItem(this.flatNodeMap.get(this.dragNode));
      this.treeControl.expandDescendants(this.nestedNodeMap.get(newItem));
    }
    this.dragNode = null;
    this.dragNodeExpandOverNode = null;
    this.dragNodeExpandOverTime = 0;
  }

  handleDragEnd(event) {
    this.dragNode = null;
    this.dragNodeExpandOverNode = null;
    this.dragNodeExpandOverTime = 0;
    this.newItem = null;
    this.isNewItem = false;
  }

  selectionChange(event){
    this.database.dataChange.next(TREE_DATA[event[0].value])
  }
}
