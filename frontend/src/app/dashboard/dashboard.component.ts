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

import { Component, OnInit } from '@angular/core';

/**
 *
 * @class DashboardComponent
 *
 * Component representing the dashboard tab (no functionality right now)
 *
 */
@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent{
  theme: string;
  pieOptions = {
    title: {
      text: 'Tagged/Untagged Documents',
      x: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b} : {c} ({d}%)'
    },
    legend: {
      x: 'center',
      y: 'bottom',
      data: ['Tagged Documents', 'Untagged Documents']
    },
    calculable: true,
    series: [
      {
        name: 'area',
        type: 'pie',
        radius: [70, 110],
        data: [
          { value: 10, name: 'Tagged Documents' },
          { value: 90, name: 'Untagged Documents' }
        ]
      }
    ]
  };

  barOptions = {
    color: ['#3398DB'],
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        axisTick: {
          alignWithLabel: true
        }
      }
    ],
    yAxis: [{
      type: 'value'
    }],
    series: [{
      name: 'Documents Added',
      type: 'bar',
      barWidth: '60%',
      data: [3, 5, 10, 3, 5, 2, 4]
    }]
  };

  options = [
    {value: 'days', viewValue: 'Days (last 7 days)'},
    {value: 'Weeks', viewValue: 'Weeks (last 4 weeks)'},
    {value: 'months', viewValue: 'Months (last 12 months)'},
    {value: 'years', viewValue: 'Years (since start)'}
  ];
  changeBar = (event) => {
    console.log("here")
    console.log(event.target.value)
  }
}
