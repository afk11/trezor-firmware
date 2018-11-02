"""
Multilayer Linkable Spontaneous Anonymous Group (MLSAG)
Optimized versions with incremental hashing.
Both Simple and Full Monero tx types are supported.

See https://eprint.iacr.org/2015/1098.pdf for details.
Also explained in From Zero to Monero section 3.3 and 5.

----------

Please note, that the MLSAG code is written in a generic manner,
where it is designed for multiple public keys (aka inputs). In another
words, MLSAG should be used to sign multiple inputs, but that is currently
not the case of Monero, where the inputs are signed one by one.
So the public keys matrix has always two rows (one for public keys,
one for commitments), although the algorithm is designed for `n` rows.

This has one unfortunate effect where `rows` is always equal to 2 and
dsRows always to 1, but the algorithm is still written as the numbers
are arbitrary. That's why there are loops such as `for i in range(dsRows)`
where it is run only once currently.

----------

Also note, that the matrix of public keys is indexed by columns first.
This is because the code was ported from the official Monero client,
which is written in C++ and where it does have some memory advantages.

For ring size = 3 and one input the matrix M will look like this:
|------------------------|------------------------|------------------------|
| public key 0           | public key 1           | public key 2           |
| cmt 0 - pseudo_out cmt | cmt 1 - pseudo_out cmt | cmt 2 - pseudo_out cmt |

and `sk` is equal to:
|--------------|-----------------------------------------------------|
| private key* | input secret key's mask - pseudo_out's mask (alpha) |

* corresponding to one of the public keys (`index` denotes which one)

----------

Mostly ported from official Monero client, but also inspired by Mininero.
Author: Dusan Klinec, ph4r05, 2018
"""

import gc

from trezor import utils

from apps.monero.xmr import crypto
from apps.monero.xmr.serialize import int_serialize


def generate_mlsag_full(
    message,
    pubs,
    in_sk,
    out_sk_mask,
    out_pk_commitments,
    kLRki,
    index,
    txn_fee_key,
    mg_buff,
):
    cols = len(pubs)
    if cols == 0:
        raise ValueError("Empty pubs")
    rows = len(pubs[0])
    if rows == 0:
        raise ValueError("Empty pub row")
    for i in range(cols):
        if len(pubs[i]) != rows:
            raise ValueError("pub is not rectangular")

    if len(in_sk) != rows:
        raise ValueError("Bad inSk size")
    if len(out_sk_mask) != len(out_pk_commitments):
        raise ValueError("Bad outsk/putpk size")

    sk = _key_vector(rows + 1)
    M = _key_matrix(rows + 1, cols)
    for i in range(rows + 1):
        sk[i] = crypto.sc_0()

    tmp_mi_rows = crypto.new_point(None)
    tmp_pt = crypto.new_point(None)

    for i in range(cols):
        crypto.identity_into(tmp_mi_rows)  # M[i][rows]

        for j in range(rows):
            M[i][j] = pubs[i][j].dest
            crypto.point_add_into(
                tmp_mi_rows,
                tmp_mi_rows,
                crypto.decodepoint_into(tmp_pt, pubs[i][j].commitment),
            )
        pubs[i] = None

        for j in range(len(out_pk_commitments)):
            crypto.point_sub_into(
                tmp_mi_rows,
                tmp_mi_rows,
                crypto.decodepoint_into(tmp_pt, out_pk_commitments[j]),
            )  # subtract output Ci's in last row

        # Subtract txn fee output in last row
        crypto.point_sub_into(tmp_mi_rows, tmp_mi_rows, txn_fee_key)
        M[i][rows] = crypto.encodepoint(tmp_mi_rows)

    sk[rows] = crypto.sc_0()
    for j in range(rows):
        sk[j] = in_sk[j].dest
        crypto.sc_add_into(sk[rows], sk[rows], in_sk[j].mask)  # add masks in last row

    for j in range(len(out_pk_commitments)):
        crypto.sc_sub_into(
            sk[rows], sk[rows], out_sk_mask[j]
        )  # subtract output masks in last row

    del (pubs, tmp_mi_rows, tmp_pt)
    gc.collect()

    return generate_mlsag(message, M, sk, kLRki, index, rows, mg_buff)


def generate_mlsag_simple(message, pubs, in_sk, a, cout, kLRki, index, mg_buff):
    """
    MLSAG for RctType.Simple
    :param message: the full message to be signed (actually its hash)
    :param pubs: vector of MoneroRctKey; this forms the ring; point values in encoded form; (dest, mask) = (P, C)
    :param in_sk: CtKey; spending private key with input commitment mask (original); better_name: input_secret_key
    :param a: mask from the pseudo output commitment; better name: pseudo_out_alpha
    :param cout: pseudo output commitment; point, decoded; better name: pseudo_out_c
    :param kLRki: used only in multisig, currently not implemented
    :param index: specifies corresponding public key to the `in_sk` in the pubs array
    :param mg_buff: buffer to store the signature to
    """
    # Monero signs inputs separately, so `rows` always equals 2 (pubkey, commitment)
    # and `dsRows` is always 1 (denotes where the pubkeys "end")
    rows = 2
    dsRows = 1
    cols = len(pubs)
    if cols == 0:
        raise ValueError("Empty pubs")

    sk = _key_vector(rows)
    M = _key_matrix(rows, cols)

    sk[0] = in_sk.dest
    sk[1] = crypto.sc_sub(in_sk.mask, a)
    tmp_pt = crypto.new_point()

    for i in range(cols):
        crypto.point_sub_into(
            tmp_pt, crypto.decodepoint_into(tmp_pt, pubs[i].commitment), cout
        )

        M[i][0] = pubs[i].dest
        M[i][1] = crypto.encodepoint(tmp_pt)
        pubs[i] = None

    del (pubs)
    gc.collect()

    return generate_mlsag(message, M, sk, kLRki, index, dsRows, mg_buff)


def gen_mlsag_assert(pk, xx, kLRki, index, dsRows):
    """
    Conditions check
    """
    cols = len(pk)
    if cols <= 1:
        raise ValueError("Cols == 1")
    if index >= cols:
        raise ValueError("Index out of range")

    rows = len(pk[0])
    if rows == 0:
        raise ValueError("Empty pk")

    for i in range(cols):
        if len(pk[i]) != rows:
            raise ValueError("pk is not rectangular")
    if len(xx) != rows:
        raise ValueError("Bad xx size")
    if dsRows > rows:
        raise ValueError("Bad dsRows size")
    if kLRki and dsRows != 1:
        raise ValueError("Multisig requires exactly 1 dsRows")
    if kLRki:
        raise NotImplementedError("Multisig not implemented")
    return rows, cols


def generate_first_c_and_key_images(message, pk, xx, kLRki, index, dsRows, rows, cols):
    """
    MLSAG computation - the part with secret keys
    :param message: the full message to be signed (actually its hash)
    :param pk: matrix of public keys and commitments
    :param xx: input secret array composed of a private key and commitment mask
    :param kLRki: used only in multisig, currently not implemented
    :param index: specifies corresponding public key to the `xx`'s private key in the `pk` array
    :param dsRows: row number where the pubkeys "end" (and commitments follow)
    :param rows: total number of rows
    :param cols: size of ring
    """
    II = _key_vector(dsRows)
    alpha = _key_vector(rows)

    tmp_buff = bytearray(32)
    Hi = crypto.new_point()
    aGi = crypto.new_point()
    aHPi = crypto.new_point()
    hasher = _hasher_message(message)

    for i in range(dsRows):
        # this is somewhat extra as compared to the Ring Confidential Tx paper
        # see footnote in From Zero to Monero section 3.3
        hasher.update(pk[index][i])
        if kLRki:
            raise NotImplementedError("Multisig not implemented")
            # alpha[i] = kLRki.k
            # rv.II[i] = kLRki.ki
            # hash_point(hasher, kLRki.L, tmp_buff)
            # hash_point(hasher, kLRki.R, tmp_buff)

        else:
            crypto.hash_to_point_into(Hi, pk[index][i])
            alpha[i] = crypto.random_scalar()
            # L = alpha_i * G
            crypto.scalarmult_base_into(aGi, alpha[i])
            # Ri = alpha_i * H(P_i)
            crypto.scalarmult_into(aHPi, Hi, alpha[i])
            # key image
            II[i] = crypto.scalarmult(Hi, xx[i])
            _hash_point(hasher, aGi, tmp_buff)
            _hash_point(hasher, aHPi, tmp_buff)

    for i in range(dsRows, rows):
        alpha[i] = crypto.random_scalar()
        # L = alpha_i * G
        crypto.scalarmult_base_into(aGi, alpha[i])
        # for some reasons we omit calculating R here, which seems
        # contrary to the paper, but it is in the Monero official client
        # see https://github.com/monero-project/monero/blob/636153b2050aa0642ba86842c69ac55a5d81618d/src/ringct/rctSigs.cpp#L191
        hasher.update(pk[index][i])
        _hash_point(hasher, aGi, tmp_buff)

    # the first c
    c_old = hasher.digest()
    c_old = crypto.decodeint(c_old)
    return c_old, II, alpha


def generate_mlsag(message, pk, xx, kLRki, index, dsRows, mg_buff):
    """
    Multilayered Spontaneous Anonymous Group Signatures (MLSAG signatures)

    :param message: the full message to be signed (actually its hash)
    :param pk: matrix of public keys and commitments
    :param xx: input secret array composed of a private key and commitment mask
    :param kLRki: used only in multisig, currently not implemented
    :param index: specifies corresponding public key to the `xx`'s private key in the `pk` array
    :param dsRows: separates pubkeys from commitment
    :param mg_buff: mg signature buffer
    """
    rows, cols = gen_mlsag_assert(pk, xx, kLRki, index, dsRows)
    rows_b_size = int_serialize.uvarint_size(rows)
    cols_b_size = int_serialize.uvarint_size(cols)
    int_serialize.dump_uvarint_b_into(cols, mg_buff)

    # Computes offset to the mg_buffer
    # mg_buffer format: (("ss", KeyM), ("cc", ECKey))
    # ss[i][j], i over cols, j over rows
    def buff_offset(col):
        return cols_b_size + col * (rows_b_size + rows * 32)

    cc = crypto.new_scalar()  # rv.cc
    c = crypto.new_scalar()
    L = crypto.new_point()
    R = crypto.new_point()
    Hi = crypto.new_point()

    # calculates the "first" c, key images and random scalars alpha
    c_old, II, alpha = generate_first_c_and_key_images(
        message, pk, xx, kLRki, index, dsRows, rows, cols
    )

    i = (index + 1) % cols
    if i == 0:
        crypto.sc_copy(cc, c_old)

    ss = [crypto.new_scalar() for _ in range(rows)]
    tmp_buff = bytearray(32)

    while i != index:
        hasher = _hasher_message(message)

        # Serialize size of the row
        offset = buff_offset(i)
        int_serialize.dump_uvarint_b_into(rows, mg_buff, offset)
        offset += rows_b_size

        for x in ss:
            crypto.random_scalar(x)

        for j in range(dsRows):
            # L = rv.ss[i][j] * G + c_old * pk[i][j]
            crypto.add_keys2_into(
                L, ss[j], c_old, crypto.decodepoint_into(Hi, pk[i][j])
            )
            crypto.hash_to_point_into(Hi, pk[i][j])

            # R = rv.ss[i][j] * H(pk[i][j]) + c_old * Ip[j]
            crypto.add_keys3_into(R, ss[j], Hi, c_old, II[j])

            hasher.update(pk[i][j])
            _hash_point(hasher, L, tmp_buff)
            _hash_point(hasher, R, tmp_buff)

        for j in range(dsRows, rows):
            # again, omitting R here as discussed above
            crypto.add_keys2_into(
                L, ss[j], c_old, crypto.decodepoint_into(Hi, pk[i][j])
            )
            hasher.update(pk[i][j])
            _hash_point(hasher, L, tmp_buff)

        for si in range(rows):
            crypto.encodeint_into(tmp_buff, ss[si])
            utils.memcpy(mg_buff, offset + 32 * si, tmp_buff, 0, 32)

        crypto.decodeint_into(c, hasher.digest())
        crypto.sc_copy(c_old, c)
        pk[i] = None
        i = (i + 1) % cols

        if i == 0:
            crypto.sc_copy(cc, c_old)
        gc.collect()

    del II

    # Finalizing rv.ss by processing rv.ss[index]
    offset = buff_offset(index)
    int_serialize.dump_uvarint_b_into(rows, mg_buff, offset)
    offset += rows_b_size

    for j in range(rows):
        crypto.sc_mulsub_into(ss[j], c, xx[j], alpha[j])
        crypto.encodeint_into(tmp_buff, ss[j])
        utils.memcpy(mg_buff, offset + 32 * j, tmp_buff, 0, 32)

    # rv.cc
    utils.memcpy(mg_buff, len(mg_buff) - 32, crypto.encodeint_into(tmp_buff, cc), 0, 32)
    utils.ensure(buff_offset(cols) + 32 == len(mg_buff), "Invalid mg_buff size")


def _key_vector(rows):
    return [None] * rows


def _key_matrix(rows, cols):
    """
    first index is columns (so slightly backward from math)
    """
    rv = [None] * cols
    for i in range(0, cols):
        rv[i] = _key_vector(rows)
    return rv


def _generate_random_vector(n):
    """
    Generates vector of random scalars
    """
    return [crypto.random_scalar() for _ in range(0, n)]


def _hasher_message(message):
    """
    Returns incremental hasher for MLSAG
    """
    ctx = crypto.get_keccak()
    ctx.update(message)
    return ctx


def _hash_point(hasher, point, tmp_buff):
    crypto.encodepoint_into(tmp_buff, point)
    hasher.update(tmp_buff)
