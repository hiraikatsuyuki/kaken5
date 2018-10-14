import configparser
import json
import os
import sys
from socket import gethostname

import pandas as pd
import pymysql
import sqlalchemy as sa
from flask import Blueprint, Flask, render_template, request
from scipy import stats
from sqlalchemy import create_engine

benchmark = Blueprint('benchmark', __name__)

config = configparser.ConfigParser()
with benchmark.open_resource('../settings/config.ini', mode='r') as f:
    config.read_string(f.read())
engine = create_engine(config['mariadb']['DATABASE_URI'])


@benchmark.route('/')
def index():
    """フロントページを作る"""
    return render_template('frontpage.j2')

@benchmark.route('/about')
def about():
    """aboutのページを作る"""
    return render_template('about.j2')


@benchmark.route('/aggregate')
def aggregate():
    """各分科の研究機関ごとの採択件数の一覧を出力する"""
    bunka = request.args.get('bunka')
    with benchmark.open_resource('sql/aggregate.sql', mode='r') as f:
        sql = f.read()
    params = {
        'bunka': bunka,
    }
    df = pd.read_sql(sa.text(sql), engine, params=params)
    df = df.assign(ranking=len(df.total)-stats.mstats.rankdata(df.total)+1)
    df = df.sort_values('total', ascending=False)
    df = df.astype({
        'ranking': int,
    })

    return render_template('aggregate.j2', bunka=bunka, df=df)


def common_aggregate(bunka, institution_list, target):
    """集計の共通部分。分科、機関リスト、集計対象を指定して、整形済みのクロス集計表を作る"""
    with benchmark.open_resource('sql/common_aggregate.sql', mode='r') as f:
        sql = f.read()
    params = {
        'bunka': bunka,
        'institution_list': institution_list,
    }
    # 件数について、機関と種目のクロス集計表を作成
    df = pd.read_sql(sa.text(sql), engine, params=params)
    pivot = df.pivot_table(values=target, index='institution_name',
                           columns='category_name', aggfunc='sum', margins=True)
    # 行の補正
    set_ab = set(institution_list) - set(list(pivot.index))
    list_ab = list(set_ab)
    df_added = pd.DataFrame(index=list_ab)
    pivot = pivot.append(df_added)
    pivot = pivot.drop(index='All')
    pivot = pivot.sort_values(by='All', ascending=False)
    # 列の補正
    columnlist = ['基盤研究(S)', '基盤研究(A)', '基盤研究(B)', '基盤研究(C)',
                  '若手研究(A)', '若手研究(B)', '挑戦的萌芽研究', 'All']
    set_ab = set(columnlist) - set(list(pivot.columns))
    list_ab = list(set_ab)
    df_added = pd.DataFrame(columns=list_ab)
    pivot = pivot.join(df_added)
    pivot = pivot.fillna(0)
    pivot = pivot[['基盤研究(S)', '基盤研究(A)', '基盤研究(B)', '基盤研究(C)',
                   '若手研究(A)', '若手研究(B)', '挑戦的萌芽研究', 'All']]
    pivot = pivot.rename(columns={
        '基盤研究(S)': 'kibanS',
        '基盤研究(A)': 'kibanA',
        '基盤研究(B)': 'kibanB',
        '基盤研究(C)': 'kibanC',
        '若手研究(A)': 'wakateA',
        '若手研究(B)': 'wakateB',
        '挑戦的萌芽研究': 'houga',
        'All': 'all',
    })
    # データ型変換
    pivot = pivot.astype({'kibanS': int, 'kibanA': int, 'kibanB': int,
                          'kibanC': int, 'wakateA': int, 'wakateB': float,
                          'houga': int, 'all': float,
                          })

    if target == 'kingaku':
        pivot = pivot.astype({
            'wakateB': int,
            'all': int,
        })

    return pivot


def make_chart_by(pivot):
    """ピボットテーブルからHighchartグラフ描画用JSONを出力する"""
    pivot = pivot.drop('all', axis=1)
    pivot = pivot.rename(columns={
        'kibanS': '基盤S', 'kibanA': '基盤A', 'kibanB': '基盤B', 'kibanC': '基盤C',
        'wakateA': '若手A', 'wakateB': '若手B', 'houga': '萌芽',
    })
    chart = {
        'chart': {
            'type': 'column'
        },
        'title': {
            'text': ''
        },
        'xAxis': {
            'categories': list(
                index[0:4] for index in pivot.index
            )
        },
        'yAxis': {
            'min': 0,
            'title': {
                'text': '',
            },
        },

        'colors': [
            "#f0e0c0", "#d0f0c0", "#c0f0e0",
            "#c0d0f0", "#e0c0f0", "#f0c0d0", "#f0c8c0",
        ],
        'series': list(
            {'name': col, 'data': item.tolist()} for col, item in pivot.iteritems()
        ),
        'plotOptions': {
            'series': {
                'stacking': 'normal',
            },
        },
    }
    dump = json.dumps(chart)

    return dump


@benchmark.route('/pivot')
def pivot():
    """件数や金額の集計"""
    # フォームの値を受け取る
    bunka = request.args.get('bunka')
    institution_list = request.args.getlist('institution')
    # 件数の集計とチャート用JSON作成
    kensuu_pivot = common_aggregate(bunka, institution_list, 'kensuu')
    kensuu_json = make_chart_by(kensuu_pivot)
    # 金額の集計とチャート用JSON作成
    kingaku_pivot = common_aggregate(bunka, institution_list, 'kingaku')
    kingaku_json = make_chart_by(kingaku_pivot)

    return render_template('pivot.j2', bunka=bunka, kensuu_pivot=kensuu_pivot, kensuu_json=kensuu_json,
                           kingaku_pivot=kingaku_pivot, kingaku_json=kingaku_json)


@benchmark.route('/projectlist')
def projectlist():
    bunka = request.args.get('bunka')
    institution = request.args.get('institution')
    category = request.args.get('category')
    with benchmark.open_resource('sql/projectlist.sql', mode='r') as f:
        sql = f.read()
    params = {
        'bunka': bunka,
        'institution': institution,
        'category': category,
    }
    df = pd.read_sql(sa.text(sql), engine, params=params)

    return render_template('projectlist.j2', bunka=bunka,
                           institution=institution, category=category, df=df)
