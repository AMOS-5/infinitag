import {Component, OnInit} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../environments/environment';
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


  constructor(private httpClient: HttpClient) {
  }
  public ngOnInit(): void {
    this.httpClient.get(this.backendStatus)
      .subscribe((value: { status: string }) => {
        this.serverStatus = value.status;
      });
  }
}
