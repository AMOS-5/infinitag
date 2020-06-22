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

import { Component, OnInit, Injectable, Inject, ViewChild, ElementRef } from '@angular/core';
import { CdkDragDrop, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA, MatDialogClose } from '@angular/material/dialog';
import { ApiService } from '../services/api.service';
import { FlatTreeControl } from '@angular/cdk/tree';
import { MatTreeFlatDataSource, MatTreeFlattener } from '@angular/material/tree';
import { BehaviorSubject } from 'rxjs';
import { FormGroup, FormBuilder } from '@angular/forms';
import { throwError } from 'rxjs';

import { IKeyWordModel } from '../models/IKeyWordModel.model';



/**
 * Type of the item of a node
 */
const NodeType = {
  DIMENSION : "DIMENSION",
  KEYWORD : "KEYWORD",
}
/**
 * Node for item
 */
export class ItemNode {
  children: ItemNode[];
  item: string;
  nodeType: string;
}

/** Flatitem node with expandable and level information */
export class ItemFlatNode {
  item: string;
  level: number;
  expandable: boolean;
  nodeType: string;
}

/**
 * The Json object for list data.
 */
let TREE_DATA: any = [];


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
    this.api.getKeywordModels()
    .subscribe((data: Array<IKeyWordModel>) => {
      for (var i = 0 ; i < data.length; i++){
        TREE_DATA[i] = JSON.parse(data[i].hierarchy);
      }

      // Notify the change.
      //this.dataChange.next(TREE_DATA[0])
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

  /** Adds a root node */
  insertRoot(name: string, nodeType: string): ItemNode {
    const newItem = { item: name, nodeType: nodeType, children: []} as ItemNode;
    this.data[0] = newItem
    this.dataChange.next(this.data);
    return newItem;
  }

  /** Add an item to list */
  insertItem(parent: ItemNode, name: string, nodeType: string): ItemNode {
    if (!parent.children) {
      parent.children = [];
    }
    const newItem = { item: name, nodeType: nodeType } as ItemNode;
    parent.children.push(newItem);
    this.dataChange.next(this.data);
    return newItem;
  }

  insertItemAbove(node: ItemNode, name: string, nodeType: string): ItemNode {
    const parentNode = this.getParentFromNodes(node);
    const newItem = { item: name, nodeType: nodeType } as ItemNode;
    if (parentNode != null) {
      parentNode.children.splice(parentNode.children.indexOf(node), 0, newItem);
    } else {
      this.data.splice(this.data.indexOf(node), 0, newItem);
    }
    this.dataChange.next(this.data);
    return newItem;
  }

  insertItemBelow(node: ItemNode, name: string, nodeType: string): ItemNode {
    const parentNode = this.getParentFromNodes(node);
    const newItem = { item: name, nodeType: nodeType } as ItemNode;
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
      newItem = this.insertItem(to, listItem.item, listItem.nodeType);
    } else {
      newItem = this.insertItem(to, from.item, from.nodeType);
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
      newItem = this.insertItemAbove(to, listItem.item, listItem.nodeType);
    } else {
      newItem = this.insertItemAbove(to, from.item, from.nodeType);
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
      newItem = this.insertItemBelow(to, listItem.item, listItem.nodeType);
    } else {
      newItem = this.insertItemBelow(to, from.item, from.nodeType);
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

  /**
  * @description
  * Returns the start node and all of its descendants
  * @param {ItemNode} start node
  * @returns {List[ItemNode]} List of the start node and all descendants
  */
  getDescendants(node: ItemNode) {
    let ret = []
    let toCheck = [node]
    while(toCheck.length !== 0) {
      let cur = toCheck.pop();
      ret.push(cur);
      if(cur.children) {
        toCheck = toCheck.concat(cur.children);
      }
    }
    return ret;
  }
}

@Component({
  selector: 'app-keywords',
  templateUrl: './keywords.component.html',
  styleUrls: ['./keywords.component.scss'],
  providers: [ChecklistDatabase]
})
export class KeywordsComponent implements OnInit {
  NodeType = NodeType; //add enum as variable so it is usable in html file

  /** contains the input string for the new dimension input field */
  newDimension: string;

  /** contains the input string for the new keyword input field */
  newKeyword: string;

  /** array of the uncategorized dimensions */
  uncatDimensions = [];

  /** array of the uncategorized keywords */
  uncatKeywords = [];

  /** array of the keywordModels */
  keywordModels: Array<IKeyWordModel> = [];

  isNewItem:boolean = false;
  newItem:any;

  /**
   * Currently selected tree data.
   */
  selectedKwmIdx: number = -1;

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

  save = true;

  /* Drag and drop */
  dragNode: any;
  dragNodeExpandOverWaitTimeMs = 300;
  dragNodeExpandOverNode: any;
  dragNodeExpandOverTime: number;
  dragNodeExpandOverArea: string;
  @ViewChild('emptyItem') emptyItem: ElementRef;

  constructor(private api: ApiService,
              private snackBar: MatSnackBar,
              private database: ChecklistDatabase,
              public dialog: MatDialog) {
    this.treeFlattener = new MatTreeFlattener(this.transformer, this.getLevel, this.isExpandable, this.getChildren);
    this.treeControl = new FlatTreeControl<ItemFlatNode>(this.getLevel, this.isExpandable);
    this.dataSource = new MatTreeFlatDataSource(this.treeControl, this.treeFlattener);

    database.dataChange.subscribe(data => {
      this.dataSource.data = [];
      this.dataSource.data = data;

      if(this.selectedKwmIdx !== -1) {
        this.keywordModels[this.selectedKwmIdx].hierarchy = this.dataSource.data;
        this.api.addKeywordModel(this.keywordModels[this.selectedKwmIdx]).subscribe(res => {

        });
      }
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
    flatNode.nodeType = node.nodeType;
    this.flatNodeMap.set(flatNode, node);
    this.nestedNodeMap.set(node, flatNode);
    return flatNode;
  }

  ngOnInit(): void {
    this.api.getKeywordModels()
    .subscribe((data: []) => {
      this.keywordModels = data;
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

  /**
  * @description
  * Opens a dialog for inputing a name. If the name is valid a new empty
  * keyword model is created.
  * @param {IKeyWordModel} kwm to remove
  */
  public newKeywordModel() {
    const dialogRef = this.dialog.open(KWMNameDialog, {
      width: '300px',
    });

    dialogRef.afterClosed().subscribe(result => {
      let name = result;

      if(name === "" || name === undefined) {
        //invalid name
        this.snackBar.open(`invalid name`, '', { duration: 3000 });
      } else if(this.keywordModels.filter(function(kwm){ return kwm.id === name }).length !== 0) {
        //duplicate
        this.snackBar.open(`${name} already exists`, '', { duration: 3000 });
      } else {
        //add new kwm
        let newKwm: IKeyWordModel = {id: name, hierarchy: [], keywords: []};
        this.api.addKeywordModel(newKwm).subscribe(res => {
          const newIdx = this.keywordModels.length;
          this.keywordModels[newIdx] = newKwm;
          TREE_DATA[newIdx] = newKwm.hierarchy;
          this.snackBar.open(`added new kwm with name: ${name}`, '', { duration: 3000 });
        });

      }
    })
  }

  /**
  * @description
  * Deletes an keyword model.
  * @param {IKeyWordModel} kwm to remove
  */
  public removeKeywordModel(keywordModel: IKeyWordModel) {
    this.api.removeKeywordModel(keywordModel).subscribe(res => {
      const removeIdx = this.selectedKwmIdx;
      this.keywordModels.splice(removeIdx, 1);
      TREE_DATA.splice(removeIdx, 1);
      this.selectedKwmIdx = -1;
      this.snackBar.open(`removed kwm with name: ${keywordModel.id}`, '', { duration: 3000 });

      this.database.dataChange.next([])
    });



    //keywordModel.hierarchy = [{ item: "root", nodeType: NodeType.DIMENSION, children: []} as ItemNode];
    //this.dragNode = undefined;
    /*this.save = false;
    const root = this.nestedNodeMap.get(this.keywordModels[this.selectedKwmIdx].hierarchy[0])
    for(let i = 0; i < 1000; i++) {
      if(i === 1000) this.save = true;

      this.handleDragStart(null, i.toString(), true, NodeType.KEYWORD);

      this.dragNodeExpandOverArea = "center";
      this.handleDrop(null, root)
      this.handleDragEnd(null);
    }*/

  }

  /**
  * @description
  * Deletes an item and all it descendants. Adds the removed keywords/dimensions
  * to their respective lists if necessary.
  * @param {ItemFlatNode} node to delete
  */
  public deleteFromHierarchy(node: ItemFlatNode) {
    const descendants = this.database.getDescendants(this.flatNodeMap.get(node))
    //re-add to uncatgegorized dimensions/keywords
    descendants.forEach(node => {
      if(node.nodeType === NodeType.DIMENSION) {
        if(!this.isDuplicate(this.uncatDimensions, node.item)) {
          this.uncatDimensions.push(node.item)
          this.api.addUncategorizedDimension(node.item)
            .subscribe(res => {});
        }
      } else if(node.nodeType === NodeType.KEYWORD) {
        if(!this.isDuplicate(this.uncatKeywords, node.item)) {
          this.uncatKeywords.push(node.item)
          this.api.addUncategorizedKeyword(node.item)
            .subscribe(res => {});
        }
        const index = this.keywordModels[this.selectedKwmIdx].keywords.indexOf(node.item, 0);
        this.keywordModels[this.selectedKwmIdx].keywords.splice(index, 1);
      } else {
        console.error("undefined type")
      }
    });
    this.removeItem(node)

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

  removeItem(flatNode: ItemFlatNode) {
    const node = this.flatNodeMap.get(flatNode)
    this.database.deleteItem(node)
  }

  /** Select the category so we can insert the new item. */
  addNewItem(node: ItemFlatNode) {
    const parentNode = this.flatNodeMap.get(node);
    this.database.insertItem(parentNode, '', node.nodeType);
    this.treeControl.expand(node);
  }

  /**
   * Handles dragOver of the mat-grid-tile
   * @param event
   */
  dragOverEmptyTree(event) {
    event.preventDefault();
  }

  /**
   * handles dropping an item over the mat-grid-tile if the tree is empty
   * @param event
   */
  dropOverEmptyTree(event) {
    if(this.selectedKwmIdx !== -1) {
      if(this.keywordModels[this.selectedKwmIdx].hierarchy.length === 0) {
        if(this.newItem.nodeType === NodeType.DIMENSION) {
          this.database.insertRoot(this.newItem.item, this.newItem.nodeType);
        } else {
          this.snackBar.open(`Root node must be a dimension`, '', { duration: 3000 });
        }
      }
    }
  }

  handleDragStart(event, node, newItem, type?) {
    if(newItem) {
      this.dragNode = new ItemFlatNode;
      this.dragNode.item = node;
      this.dragNode.nodeType = type;
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

  /**
   * Handles dropping an item over the another node.
   * Before moving the node, the correctness of the resulting tree is ensured.
   * @param event
   * @param node that the dragNode is dropped over
   */
  handleDrop(event, node) {
    if (node !== this.dragNode) {
      let newItem: ItemNode = null;
      console.log("dragNode", this.flatNodeMap.get(this.dragNode), "node", this.flatNodeMap.get(node), "newItem", this.newItem)
      if(this.newItem !== null
         && this.newItem.nodeType === NodeType.KEYWORD
         && this.keywordModels[this.selectedKwmIdx].keywords.includes(this.newItem.item)) {
        this.snackBar.open(`${this.newItem.item} is already in this keyword model`, '', { duration: 3000 });
      } else {
        //dragNode is used if the item is moved within the tree, this.newItem otherwise
        let nodeToDrop = this.dragNode === undefined ? this.newItem : this.dragNode;
        if (this.dragNodeExpandOverArea === 'above') {
          if(nodeToDrop.nodeType === node.nodeType) { // must be same node type as sibling
            newItem = this.database.copyPasteItemAbove(this.flatNodeMap.get(this.dragNode), this.flatNodeMap.get(node), this.newItem);
          } else {
            this.snackBar.open(`${nodeToDrop.item} must be a ${node.nodeType} to be moved here`, '', { duration: 3000 });
          }
        } else if (this.dragNodeExpandOverArea === 'below') {
          if(nodeToDrop.nodeType === node.nodeType) {// must be same node type as sibling
            newItem = this.database.copyPasteItemBelow(this.flatNodeMap.get(this.dragNode), this.flatNodeMap.get(node), this.newItem);
          } else {
            this.snackBar.open(`${nodeToDrop.item} must be a ${node.nodeType} to be moved here`, '', { duration: 3000 });
          }
        } else {
          if(nodeToDrop.nodeType !== node.nodeType) {// must be different node type as parent
            newItem = this.database.copyPasteItem(this.flatNodeMap.get(this.dragNode), this.flatNodeMap.get(node), this.newItem);
          } else {
            this.snackBar.open(`A ${nodeToDrop.nodeType} can not be added to a  ${node.nodeType}`, '', { duration: 3000 });
          }
        }
      }
      if(newItem !== null) {
        if(newItem.nodeType === NodeType.KEYWORD) { //add to keywords list
          this.keywordModels[this.selectedKwmIdx].keywords.push(newItem.item);
        }
        this.database.deleteItem(this.flatNodeMap.get(this.dragNode)); //remove old node
        this.treeControl.expandDescendants(this.nestedNodeMap.get(newItem));
      }
    }
    //cleanup
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
    this.selectedKwmIdx = event[0].value;
    this.database.dataChange.next(TREE_DATA[this.selectedKwmIdx]);
  }
}


@Component({
  selector: 'input-dialog',
  templateUrl: 'input-dialog.html',
})
export class KWMNameDialog {

  constructor(
    public dialogRef: MatDialogRef<KWMNameDialog>,
    @Inject(MAT_DIALOG_DATA) public name: string) {}

  onClose(): void {
    this.dialogRef.close();
  }
}